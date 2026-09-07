## Context

当前诊断能力只有 `Student.barrier_profile`（JSON）+ `barrier_updated_at` 两个空壳字段，无作答记录、无枚举、无 LLM 客户端。代码库已有约定骨架：化学技能按领域模块放在 `chem_skills/<domain>/engine/`（参照已建成的 `chemistry_audit/engine/`），其中 `chemistry_diagnosis/engine/` 已预置占位。LLM 选型见 38 号文档：三级 fallback `MiMo-V2.5 → qwen-turbo → DeepSeek-V4-Flash`，每级 3 次重试 + 指数退避；config 仅配置了 DashScope 的 embedding key，对话客户端需新建。动机与范围见 proposal.md。

## Goals / Non-Goals

**Goals:**
- 后端诊断核心端到端走通：作答记录 → 双维度诊断 → 学生/班级画像 → 教师覆盖。
- 遵循既有代码约定：中文 docstring、枚举小写下划线存储 + `enum_type` CHECK 约束、软删除 mixin、Alembic 迁移、TDD 三级测试。
- 诊断结果可追溯：`confidence` 落库，覆盖操作 append-only 审计。

**Non-Goals:**
- 不建作答采集/OCR 链路（本 change 用测试 seed 数据驱动 `StudentAnswer`）。
- 不做阈值触发的自动/实时诊断（`BarrierConfig` 只存配置，触发逻辑留待实时诊断分支）。
- 不做前端页面、不做 Agent 工具集成。
- `consecutive_errors` / `consecutive_correct` 字段按文档 27 建列，但本 change 仅维护不消费（服务于未来阈值触发，避免后续迁移）。

## Decisions

### D1：代码落位 — 引擎归 `chem_skills/`，API 归 `app/api/`

诊断引擎业务逻辑放 `chem_skills/chemistry_diagnosis/engine/`（rule_engine / llm_client / diagnosis / aggregator），与 `chemistry_audit` 骨架一致；HTTP 层放 `app/api/diagnosis.py`；模型放 `app/models/`。
- 备选：全部塞进 `app/` —— 违背既有模块划分，且让 `chem_skills/chemistry_diagnosis` 占位继续空置。
- 理由：领域逻辑与传输层分离，与现有一致。

### D2：数据模型 — 新增三表 + 扩展 Student + 两枚举

- `students` 新增 `misconception_profile`（JSON，可空），与已有 `barrier_profile` 并列。
- 新增 `student_answers`：`id`、`student_id`（FK students）、`exam_id`（FK exams，即文档的「考试记录」）、`question_id`（FK questions）、`is_correct`（bool 非空）、`student_answer`（text）、`barrier_type`（enum，可空）、`misconception_category`（enum，可空）、`confidence`（float，可空）、`consecutive_errors`/`consecutive_correct`（int 默认 0）。
- 新增 `barrier_configs`：`teacher_id`（唯一，FK teachers）、`concept_threshold`/`reading_threshold`/`expression_threshold`/`mastery_threshold`（int）、`auto_sync_to_student`（bool）。
- 新增 `diagnosis_override_logs`（append-only 审计，仿 `exam_status_transitions`）：`student_id`、`old_profile`/`new_profile`（JSON）、`reason`（text）、`operator_id`（FK teachers）、`created_at`。
- 新增 `parent_notifications`：`student_id`、`parent_id`、`type`、`content`（JSON/text）、`created_at`、`read_at`（可空）。
- 学习计划存储：`students.current_plan`（JSON，可空）。
- 枚举 `BarrierType`（concept/reading/expression）、`MisconceptionCategory`（chemical_equilibrium/redox/mole_calculation/organic_chemistry/chemical_notation/structure_properties）入 `app/core/enums.py`。

### D3：字段命名 — 以代码为源，文档 API 层映射

Student 层沿用代码已有 `barrier_profile` / `barrier_updated_at`（非文档 27 的 `barrier_type` / `barrier_last_updated`）；作答记录层用 `barrier_type` / `misconception_category` / `confidence` 三个独立字段（非 JSON）。API 响应沿用文档 Schema（`barrier_type` 对象、`dominant_barrier` 等），在 service 层从落库字段组装，避免命名漂移外泄。

### D4：LLM 服务 — 三级 fallback 对话客户端 + JSON 鲁棒解析

`llm_client.py` 定义 `DiagnosisLLMClient` Protocol（`chat(messages) -> dict`），按 `MiMo-V2.5 → qwen-turbo → DeepSeek-V4-Flash` 顺序、每级 3 次重试 + 指数退避。诊断与学习计划为纯文本任务，主用 qwen-turbo/DeepSeek；temperature 0.3。诊断 `max_tokens=2000`，学习计划 `max_tokens=4096`。

响应解析（鲁棒性三件套）：
1. 预处理：剥离 markdown 代码围栏；`json.loads` 失败时做一次容忍尾逗号的宽松解析。
2. 枚举校验：`barrier_type`/`misconception_category` 取值必须合法，非法则丢弃该字段结果。
3. 修复重试：解析/枚举失败时，带「只返回合法枚举 JSON」的 re-prompt 重试一次，仍失败才降级规则兜底（见 D9）。

注入缝：`diagnosis.py` 通过构造注入 `DiagnosisLLMClient`，单测传 `FakeLLM`（固定/非法/超时响应），单元测试零网络。
- 备选：只接单一 provider —— 违背 38 号「三级 fallback」决策，且无法满足 spec 的降级要求。

### D5：诊断流程 — 三引擎三段式（LLM 主判 + 规则三角色）

引擎分三模块串联：`rule_engine`（关键词预分类，命中给 0.5–0.7 保守置信度，未命中标 uncertain）→ `llm_client`（LLM 深度分析，返回 `{barrier_type, misconception_category, confidence, reasoning, suggestion}`）→ `confidence_fusion`（置信度融合引擎，见 D9）。规则引擎承担「上下文喂入」「兜底」两角色：预分类结果作为额外上下文传入 LLM，LLM 失败时由规则分类兜底；「矛盾校验」由融合引擎以「双候选 + needs_review 复核」承接（见 D9），完整教师审核 UI 归前端分支。`diagnosis.py` 编排整体，批量端点每次取 ≤10 条未诊断错误作答，`ThreadPoolExecutor(max_workers=5)` 并发，完成后统一 commit 再聚合。
- 备选：规则结果直接作为最终判定跳过 LLM —— 文档 27 明确「命中与未命中均进 LLM」，规则仅作兜底/上下文。

### D6：聚合算法 — 双维度独立聚合

`aggregator.py` 对每个学生：查询已诊断错误作答 → 分别按 `barrier_type` 与 `misconception_category` 计数 → 归一化为占比（保留两位小数、和约 1.0）→ 写 `barrier_profile` / `misconception_profile`（补齐缺失类型为 0）→ 更新 `barrier_updated_at`。主导障碍 `dominant_barrier` = 占比最高类型。

### D7：教师覆盖 — 90/5/5 + 审计

覆盖写指定类型 90%、其余各 5%，先落 `diagnosis_override_logs`（旧画像 + 新画像 + 原因 + 操作人），再更新学生画像与时间戳。后续新作答经聚合逐步稀释手动权重（不额外实现稀释逻辑，聚合天然覆盖）。

### D8：学习计划 — 24h 内存缓存 + 通知落库

`learning_plan` 生成后以 `student_id` 为键、`expires_at` 过期时间戳做进程内缓存；`apply` 写入 `students.current_plan`；`send-to-parent` 写入 `parent_notifications`。缓存是进程内 dict（非分布式），重启失效可接受——与文档 27 一致。

### D9：置信度融合引擎 — 二维决策表 + 冲突双候选

`confidence_fusion.py` 按「规则命中状态 × LLM 置信度」二维决策表融合规则与 LLM 信号，产出最终 `barrier_type` + `confidence`：

| | LLM 正常/高置信 | LLM 低置信(<0.7)或失败 |
|---|---|---|
| **规则命中** | 双路一致 → 取规则与 LLM 置信度较高者 | 冲突或 LLM 弱 → 默认 LLM 分类 + 保留规则候选，`needs_review=true` |
| **规则未命中** | 纯 LLM，取 LLM 值 | 双低 → 标记「建议人工复核」，不自动采纳 |

具体规则：

- 规则命中且与 LLM 一致 → 分类取该类型，`confidence = max(rule_conf, llm_conf)`（规则命中是高精确信号，不因 LLM 低置信被拖低）。
- 规则命中但与 LLM 矛盾 → 默认取 LLM 分类，同时保留规则候选 + `needs_review=true` 供教师二选一，不静默丢弃规则结论。
- 规则未命中 + LLM 正常 → 纯 LLM，`confidence` 取 LLM 值。
- 规则未命中 + LLM 低置信(<0.7) → 双低，标记「建议人工复核」，不自动采纳。
- LLM 失败/非法 → 分类取规则，`confidence` 取规则 0.5–0.7，标记「规则兜底」，迷思概念为空。

融合后的 `confidence` 进入三级分级（≥0.8 采纳 / 0.7–0.8 标记 / <0.7 复核）。迷思概念仅 LLM 产出，规则引擎不参与。

> 注：规则精确率高于 LLM 召回率这一前提，使冲突时「静默信 LLM」会浪费规则的高精确信号，故改为双候选复核。评估层（tasks §9.3，18 条标注集，3 障碍 × 6 迷思均衡）实测端到端宏观指标：障碍类型精确率 81.9% / 召回率 77.8%，迷思概念类别精确率 90.5% / 召回率 77.8%（数据 `tests/eval/labeled_dataset.json`，结果 `tests/eval/results.json`）。

### D10：规则基 — JSON 配置驱动（非 YAML）+ 接线测试守护

规则引擎的关键词按 JSON 规则文件驱动，而非 Python 硬编码：`chemistry_diagnosis/rules/barriers.json` 存 `{"concept": [...], "reading": [...], "expression": [...]}` 三组关键词，`rule_engine.py` import 时加载一次并作为唯一真相源。新增知识板块/规则 = 加一条 JSON 条目，零代码改动。

- 选 JSON 而非 YAML：仓库既有惯例是 JSON（`chemistry_audit/rules/*.json`），YAML 需新增 PyYAML 依赖且无额外收益。
- 前车之鉴：`chemistry_audit/rules/*.json` 目前是死代码（无任何 Python 加载，真实规则硬编码在 `.py` 且已漂移——`conditions.py` 9 条 vs `conditions.json` 7 条）。诊断规则基必须「接线 + 测试守护」：一条单测断言加载后规则集非空且 schema 合法（键 ∈ 三障碍类型、值非空列表），防止再次退化成死代码。
- 已知弱项：reading（审题）维度几乎无关键词信号，规则引擎对 reading 的精确率/召回率结构性偏低；接受这一局限，reading 主要由 LLM 主判 + 题目元信息（题干含数值/条件）覆盖，不靠关键词。

## Risks / Trade-offs

- [LLM 诊断输出不稳定（非 JSON / 非法枚举）] → 正则提取 + 枚举白名单校验；全部失败降级规则引擎兜底。
- [SQLite 下 ThreadPoolExecutor 并发写同一 SQLite 文件] → 批量诊断用单 session + 统一 commit；并发只发生在无状态的 LLM 调用阶段，不并发写库。
- [迷思概念类别与知识点映射粗糙] → `weak_knowledge_points` 首版从迷思概念映射到关联知识点，映射表后续可调；不阻塞诊断主链路。
- [进程内缓存非持久] → 可接受（重启重建），符合文档 27 的 24h 缓存语义。

## Open Questions

- 迷思概念是否需多标签（一条作答命中多类）？首版按单一主类别（与 `barrier_type` 对齐）实现；如需多标签，仅影响聚合与 LLM 输出结构，不改变本 design 的模块边界。
