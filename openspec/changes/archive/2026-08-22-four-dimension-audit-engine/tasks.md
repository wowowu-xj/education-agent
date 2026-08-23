## 1. 模块结构搭建

- [ ] 1.1 创建目录结构：`chem_skills/chemistry_parser/engine/`、`chem_skills/chemistry_audit/engine/`、`chem_skills/chemistry_audit/rules/`
- [ ] 1.2 创建各模块 `__init__.py`，定义公开接口

## 2. 化学式归一化

- [ ] 2.1 实现 `chem_skills/chemistry_parser/engine/normalizer.py`：箭头符号统一（→→\\rightarrow, ⇌→\\rightleftharpoons, ↑→\\uparrow, ↓→\\downarrow）
- [ ] 2.2 实现裸化学式白名单（约 50 个常见化学式）和自动 LaTeX 包装逻辑
- [ ] 2.3 实现词界保护（3+ 连续小写字母跳过）
- [ ] 2.4 编写 `tests/test_normalizer.py`：箭头转换、白名单包装、词界保护、已包装不重复

## 3. 方程式解析器

- [ ] 3.1 实现 `chem_skills/chemistry_audit/engine/parser.py`：`parse_equation()` — 按分隔符（→/=/->）拆分反应物/产物
- [ ] 3.2 实现 `split_compounds()` — 按 + 号拆分，括号嵌套保护
- [ ] 3.3 实现 `strip_coefficient()` — 剥离前导系数
- [ ] 3.4 实现 `expand_parentheses()` — 递归展开括号 (原子团)n
- [ ] 3.5 实现 `match_elements()` — 正则 `[A-Z][a-z]?` 匹配元素符号 + 下标数字
- [ ] 3.6 编写 `tests/test_parser.py`：分隔符变体、括号嵌套、系数剥离、解析错误

## 4. 维度 1：系数配平审核

- [ ] 4.1 实现 `chem_skills/chemistry_audit/engine/counter.py`：`count_elements()` — 单侧元素原子计数
- [ ] 4.2 实现 `chem_skills/chemistry_audit/engine/balance.py`：`check_balance()` — 两侧逐元素比对，输出 BalanceResult
- [ ] 4.3 有机反应检测：识别燃烧方程式自动降级为 warning
- [ ] 4.4 编写 `tests/test_balance.py`：86 道确定性测试 + 未配平拦截 + 含括号配平 + 有机反应 warning

## 5. 维度 2：反应条件审核

- [ ] 5.1 创建 `chem_skills/chemistry_audit/rules/conditions.json`：14 条件关键词 + 反应类型-条件映射表
- [ ] 5.2 实现 `chem_skills/chemistry_audit/engine/conditions.py`：`check_conditions()` — 关键词扫描 + 反应类型判断 + 矛盾检测
- [ ] 5.3 编写 `tests/test_conditions.py`：燃烧反应缺点燃、催化分解缺催化剂、非燃烧无需求、矛盾条件检测

## 6. 维度 3：产物稳定性审核

- [ ] 6.1 创建 `chem_skills/chemistry_audit/rules/precipitation.json`：8 组沉淀离子组合规则
- [ ] 6.2 创建 `chem_skills/chemistry_audit/rules/redox.json`：氧化还原产物合理性规则
- [ ] 6.3 实现 `chem_skills/chemistry_audit/engine/stability.py`：`check_stability()` — 气体逸出/沉淀/氧化还原规则匹配
- [ ] 6.4 编写 `tests/test_stability.py`：H₂CO₃ 分解、沉淀规则、浓硫酸产物验证

## 7. 维度 4：分子结构审核

- [ ] 7.1 实现 `chem_skills/chemistry_audit/engine/structure.py`：`check_structure()` — 元素符号格式、括号栈匹配、离子电荷格式、LaTeX 格式
- [ ] 7.2 编写 `tests/test_structure.py`：大小写错误、括号不匹配、电荷格式错误

## 8. 审核引擎集成

- [ ] 8.1 实现 `chem_skills/chemistry_audit/engine/models.py`：AuditReport、BalanceResult、ConditionResult、StabilityResult、StructureResult 数据类
- [ ] 8.2 实现 `chem_skills/chemistry_audit/__init__.py`：AuditEngine 单例 + `audit_equation()` 快捷函数，串联归一化→解析→四维审核
- [ ] 8.3 实现综合判定逻辑：任一维度 blocked → overall_status=blocked；warning 不触发拦截
- [ ] 8.4 编写 `tests/test_audit_engine.py`：端到端审核测试（有效方程式 passed、无效方程式 blocked、warning 不拦截）

## 9. API 层

- [ ] 9.1 创建 `app/api/audit.py`：`GET /api/audit/equation?eq=<equation_string>`，调用 audit_equation() 返回 AuditReport JSON
- [ ] 9.2 在 `app/main.py` 中注册 audit 路由
- [ ] 9.3 编写 `tests/test_audit_api.py`：有效请求 200 + 正确 JSON、无效方程式 blocked、缺参数 422、解析错误处理

## 10. 收尾

- [ ] 10.1 运行全量 pytest，确保新增测试通过且不破坏现有测试
- [ ] 10.2 运行 `openspec validate four-dimension-audit-engine` 确保变更通过校验
