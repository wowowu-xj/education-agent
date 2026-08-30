# Tasks

## 1. 后端使能端点（TDD）

- [x] 1.1 编写 `GET /api/question-sets/{id}/questions` 失败测试（RED），断言：按 sort_order 升序返回、过滤软删题、他人文件夹返回 404
- [x] 1.2 实现文件夹内题目列表端点，使 1.1 测试通过（GREEN）
- [x] 1.3 编写 `GET /api/classes` 失败测试（RED），断言：普通教师仅返回任教班级（经 TeacherClassSubject）、返回 id 与名称
- [x] 1.4 实现班级列表端点，使 1.3 测试通过（GREEN）

## 2. Tab 2 题库管理

- [x] 2.1 文件夹列表接入 `GET /api/question-sets`，卡片展示名称 + 派生题目数，替换 `BANK_ITEMS` mock
- [x] 2.2 文件夹 CRUD：新建/重命名走 `POST`/`PUT`，删除走 `DELETE`（弹确认），`is_preset` 隐藏删除入口，空态显示「新建文件夹」引导
- [x] 2.3 选中文件夹后调用 `GET /api/question-sets/{id}/questions` 展示题目卡片网格（题干摘要 + 题型 + 难度标签），空文件夹显示引导空态
- [x] 2.4 加题：文件夹详情「加入题目」入口，弹出题目选择器（复用 `/api/questions/search` + `/api/questions`），勾选后 `POST /{id}/questions`；重复加入展示冲突提示
- [x] 2.5 移题：题目卡片「移出」调 `DELETE /{id}/questions/{qid}`，仅解除关联并刷新列表

## 3. Tab 4 考试列表（Paper 视角）

- [x] 3.1 试卷列表接入 `GET /api/papers`，卡片展示标题/题目数/总分/状态（草稿=中性、已发布=Teal），替换 `EXAM_LIST` mock，空态「请先创建一份试卷」
- [x] 3.2 试卷 CRUD：创建走 `POST`、编辑走 `PUT`（locked 隐藏编辑入口）、删除走 `DELETE`（被 Exam 引用展示 409 冲突提示）
- [x] 3.3 发布试卷：draft 试卷「发布」弹班级多选（`GET /api/classes`），提交 `POST /{id}/publish`；无题试卷禁用发布并提示
- [x] 3.4 导出试卷：卡片「导出」提供 HTML 预览（新标签打开）与 DOCX 下载，走 `GET /{id}/export`
- [x] 3.5 考试状态展示：已发布试卷展开显示班级 + Exam 六态标签（`GET /api/exams` 按 paper_id 分组 + `GET /api/classes` 解析班名），取消考试走 `POST /api/exams/{id}/cancel`

## 4. 状态标签与视觉

- [x] 4.1 落地 D6 状态标签映射表（Paper 两态 + Exam 六态 → 中文 + Academic Catalyst 配色），供 Tab 4 复用

## 5. 验证

- [x] 5.1 后端测试全绿（`pytest`），`openspec validate bank-exam-list-frontend --strict` 通过
- [x] 5.2 浏览器手动验证 Tab 2 / Tab 4 全流程（列表/CRUD/发布/导出/状态标签/空态/错误态）
