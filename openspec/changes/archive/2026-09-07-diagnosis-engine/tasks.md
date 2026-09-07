# Tasks

## 1. 枚举与数据模型（TDD）

- [x] 1.1 编写枚举失败测试（RED）：`BarrierType` 仅 concept/reading/expression，`MisconceptionCategory` 仅六个合法值，非法值被拒绝
- [x] 1.2 在 `app/core/enums.py` 定义 `BarrierType`、`MisconceptionCategory`，使 1.1 通过（GREEN）
- [x] 1.3 编写 `StudentAnswer` 模型失败测试（RED）：字段齐全（student/exam/question/is_correct/student_answer/barrier_type/misconception_category/confidence/consecutive_*），诊断字段可空
- [x] 1.4 实现 `app/models/student_answer.py`，使 1.3 通过（GREEN）
- [x] 1.5 编写 `BarrierConfig`、`DiagnosisOverrideLog`、`ParentNotification` 模型失败测试（RED）
- [x] 1.6 实现三个模型，并为 `Student` 新增 `misconception_profile`、`current_plan` 字段，使 1.5 通过（GREEN）
- [x] 1.7 生成 Alembic 迁移并应用（`alembic revision` + `upgrade`）

## 2. LLM 客户端

- [x] 2.1 定义 `DiagnosisLLMClient` Protocol（`chat(messages) -> dict`），实现类通过构造注入 `diagnosis.py`
- [x] 2.2 编写 fallback 失败测试（RED）：mock 首选 Provider 失败时按 MiMo→qwen→DeepSeek 顺序回退，每级重试 3 次并指数退避
- [x] 2.3 编写 JSON 鲁棒性测试（RED）：剥离代码围栏、尾逗号宽松解析、非法枚举一次 re-prompt 后仍失败降级
- [x] 2.4 实现 `chem_skills/chemistry_diagnosis/engine/llm_client.py`（chat + 围栏剥离 + 宽松解析 + 枚举校验 + 修复重试），使 2.2/2.3 通过（GREEN）

## 3. 规则引擎（JSON 规则基）

- [x] 3.1 创建 `chem_skills/chemistry_diagnosis/rules/barriers.json`（concept/reading/expression 三组关键词），`rule_engine.py` import 时加载
- [x] 3.2 编写接线守护测试（RED）：加载后规则集非空且 schema 合法（键 ∈ 三障碍类型、值非空列表）
- [x] 3.3 编写关键词预分类失败测试（RED）：三组关键词命中给对应类型 + 0.5–0.7 保守置信度，未命中标 uncertain
- [x] 3.4 实现 `rule_engine.py`（加载 JSON + 关键词预分类），使 3.2/3.3 通过（GREEN）

## 4. 置信度融合引擎（二维决策表）

- [x] 4.1 编写融合失败测试（RED）：双路一致取高置信、冲突双候选 + needs_review、双低标记复核、LLM 失败规则兜底（迷思概念为空）
- [x] 4.2 实现 `confidence_fusion.py`（2×2 决策表纯函数），使 4.1 通过（GREEN）

## 5. 诊断编排

- [x] 5.1 编写诊断编排失败测试（RED）：规则引擎 → LLM → 融合 三引擎串联，输出最终双维度 + 置信度 + 依据 + 建议；LLM 返回非法枚举计入失败；规则结果作为上下文传入 LLM
- [x] 5.2 实现 `chem_skills/chemistry_diagnosis/engine/diagnosis.py`（编排 + ThreadPoolExecutor 并发），使 5.1 通过（GREEN）

## 6. 双维度聚合

- [x] 6.1 编写双维度聚合失败测试（RED）：按类型计数归一化、补齐缺失类型为 0、无诊断数据返回空
- [x] 6.2 实现 `chem_skills/chemistry_diagnosis/engine/aggregator.py`，使 6.1 通过（GREEN）

## 7. 诊断 API 端点

- [x] 7.1 编写批量诊断失败测试（RED）：`POST /run-llm/{exam_record_id}` 取 ≤10 条未诊断错误作答，返回 analyzed_count/failed_count
- [x] 7.2 实现 `app/api/diagnosis.py` 的 run-llm 端点，使 7.1 通过（GREEN）
- [x] 7.3 编写聚合查询失败测试（RED）：`GET /barrier/{class_id}/{exam_id}` 返回 students（含 dominant_barrier + weak_knowledge_points）与 class_barrier_distribution
- [x] 7.4 实现 barrier 端点，使 7.3 通过（GREEN）
- [x] 7.5 编写教师覆盖失败测试（RED）：`PUT /override/{student_id}` 写 90/5/5 + 记录审计日志，非法类型拒绝
- [x] 7.6 实现 override 端点，使 7.5 通过（GREEN）
- [x] 7.7 编写阈值配置失败测试（RED）：`GET/PUT /config/{teacher_id}` 默认值 + upsert
- [x] 7.8 实现 config 端点，使 7.7 通过（GREEN）
- [x] 7.9 编写查询端点失败测试（RED）：`/class/{id}/stats`、`/class/{id}/kp/{kp}`、`/history/{id}`
- [x] 7.10 实现三个查询端点，使 7.9 通过（GREEN）

## 8. 学习计划子系统

- [x] 8.1 编写计划生成 + 缓存失败测试（RED）：障碍类型中文映射、24h 缓存命中不重复调用 LLM
- [x] 8.2 实现 generate + 缓存逻辑，使 8.1 通过（GREEN）
- [x] 8.3 编写生命周期失败测试（RED）：apply 写 `students.current_plan`、send-to-parent 写 `parent_notifications`、无绑定家长报错
- [x] 8.4 实现 apply / send-to-parent / get 端点，使 8.3 通过（GREEN）

## 9. 验证

- [x] 9.1 后端测试全绿（`pytest`），`openspec validate diagnosis-engine --strict` 通过
- [x] 9.2 seed 数据端到端走通：fixture 写入 `StudentAnswer` → 三引擎诊断 → 双维度画像聚合 → 教师覆盖可回溯
- [x] 9.3 评估层：`tests/eval/` 用真实 LLM 跑标注错题集，输出每维度精确率/召回率，回填 design D9 的 90%/85% 估算值
