## 1. 数据模型与迁移

- [ ] 1.1 创建 Review 数据模型 `app/models/review.py`：review_id、question_id、status（pending/reviewing/passed/rejected）、四维评分字段（science_score、difficulty_match_score、knowledge_coverage_score、discrimination_score）、总分 total_score、未通过原因 reject_reasons（JSON）、时间戳（started_at、completed_at、created_at、updated_at）
- [ ] 1.2 在 `app/models/__init__.py` 中注册 Review 模型
- [ ] 1.3 生成 Alembic 迁移脚本并执行 upgrade，创建 review 表

## 2. 审核状态机

- [ ] 2.1 实现 `app/services/__init__.py` 模块初始化
- [ ] 2.2 实现 `app/services/review_state_machine.py`：ReviewStateMachine 类，状态转换表定义合法转换（pending→reviewing, reviewing→passed, reviewing→rejected），非法转换抛异常
- [ ] 2.3 实现评分计算函数 `calculate_total_score()`：四维等权平均（25% 每维度），阈值判断（单维度≥60 且总分≥70 为通过）

## 3. 四维审核 API

- [ ] 3.1 创建 `app/api/review.py`：定义 Pydantic request/response schema（ReviewSubmitRequest、ReviewResponse、ReviewListResponse）
- [ ] 3.2 实现 `POST /api/review/submit`：校验题目存在且无进行中审核，创建 Review 记录（status=pending），返回 review_id
- [ ] 3.3 实现 `GET /api/review/{review_id}`：返回审核详情（含四维评分和状态）
- [ ] 3.4 实现 `GET /api/review/list`：按 status 筛选 + 分页（page、page_size）
- [ ] 3.5 实现 `POST /api/review/{review_id}/process`：触发审核（占位规则引擎），状态机流转 pending→reviewing→passed/rejected
- [ ] 3.6 在 `app/main.py` 中注册 review 路由

## 4. 出题工作台前端

- [ ] 4.1 创建 `frontend/pages/question-workbench.html`：Vue 3 CDN 单文件应用骨架，引入 Tailwind CSS CDN 和 KaTeX CDN，三个 Tab 按钮（手动命题/AI生成/OCR导入）
- [ ] 4.2 实现 Tab 切换逻辑：Vue 3 `v-show` 控制三个面板显隐，当前激活 Tab 高亮样式
- [ ] 4.3 实现手动命题表单组件：题型选择器（8 种题型下拉）、题干 textarea + KaTeX 实时预览、选项编辑器（v-for 动态增减）、答案设置、解析编辑器 + KaTeX 预览、知识点标签输入、难度滑块（1-5）
- [ ] 4.4 实现 AI 生成面板（占位）：知识点选择、难度选择、题型选择、题目数量输入、生成按钮（调用预留 API）
- [ ] 4.5 实现 OCR 导入面板（占位）：文件上传区域、识别结果预览占位区
- [ ] 4.6 实现 KaTeX 混合渲染指令：Vue 自定义指令 `v-katex`，自动检测 `$...$` 和 `$$...$$` 标记并调用 katex.renderToString()
- [ ] 4.7 实现 Tailwind 响应式布局：桌面双栏（lg:grid-cols-2）、平板单栏，表单区 + 预览区
- [ ] 4.8 实现保存草稿和提交审核按钮：调用后端 API，状态提示 toast

## 5. 测试

- [ ] 5.1 编写 `tests/test_review_state_machine.py`：测试所有合法状态转换、非法转换被拒绝、评分计算阈值边界
- [ ] 5.2 编写 `tests/test_review_api.py`：测试提交审核（成功/题目不存在/重复提交）、查询详情（存在/不存在）、列表筛选分页、审核流程端到端（submit→process→verify status）
- [ ] 5.3 运行全量 pytest，确保新增测试通过且不破坏现有测试

## 6. 集成与收尾

- [ ] 6.1 在 `app/main.py` 中配置静态文件挂载路径，确保出题工作台页面可通过 `/pages/question-workbench.html` 访问
- [ ] 6.2 手动验证：启动 FastAPI 服务，浏览器访问出题工作台页面，Tab 切换正常、KaTeX 渲染正常、审核 API 返回正确
- [ ] 6.3 运行 `openspec validate question-workbench-review` 确保变更通过校验
