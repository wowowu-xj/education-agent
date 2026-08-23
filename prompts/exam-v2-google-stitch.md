# Google Stitch Prompt: Teacher Exam Workbench (exam-v2.html)

---

Generate a single, self-contained HTML file (`exam-v2.html`) for a teacher's exam workbench. It must be a 4-tab single-page application using vanilla JavaScript for tab switching — **no Vue, React, or any framework**. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Chips/tags `16px`
- **Audit badges**:
  - Pass: background `#e0f2f1`, text `#004f50`, green checkmark icon
  - Warning: background `#fff3cd`, text `#856404`, yellow warning icon
  - Blocked: background `#ffdad6`, text `#93000a`, red cross icon
- **Target viewport**: Desktop 1280px+

---

## Page Header & Tab Bar

At the very top, render **4 tab labels** in a horizontal row:

1. 出题工作台 (Question Workbench) — **default active**
2. 题库管理 (Question Bank)
3. 历史真题库 (Past Exams)
4. 考试列表 (Exam List)

The active tab has a **2px solid underline** in Oxford Blue `#002045`. Inactive tabs have no underline and use a muted gray text color. Tabs are separated by comfortable spacing (e.g., 32px gap). Clicking a tab hides all other tab panels and shows only the corresponding one — implement this with plain JavaScript `display: none/block` toggling.

---

## Tab 1 — 出题工作台 (Question Workbench) — Default Active

### Sub-mode Toggle Bar

Three toggle buttons in a segmented-control style:

- **AI生成** (AI Generate) — active by default
- **手动录入** (Manual Entry)
- **OCR导入** (OCR Import)

The active button has an **Oxford Blue `#002045` background with white text**. Inactive buttons have a light gray background with dark text. Buttons are adjacent with no gap (segmented control look), rounded corners on outer edges only.

### Question Type Chips

A row of filter chips (pill-shaped, `border-radius: 16px`):

- 选择题 (Multiple Choice)
- 填空题 (Fill in the Blank)
- 计算题 (Calculation)
- 方程式配平 (Equation Balancing)
- 实验探究 (Experiment Inquiry)

White background, `1px solid #d0d0d0` border. Selected chip gets Oxford Blue background with white text. Multiple chips can be selected.

### Difficulty Dropdown

A standard `<select>` dropdown with options: 简单 (Easy), 中等 (Medium), 困难 (Hard). Labeled "难度" (Difficulty).

### Knowledge Point Search

A full-width text input with a search (magnifying glass) icon on the left. Placeholder text: "搜索知识点..." (Search knowledge points...). Styled with a light background, subtle border, and the icon absolutely positioned or using a wrapper.

### Variant Mode Checkbox

A simple checkbox labeled "生成变体" (Generate Variants). Styled neatly.

### Generate Button

A full-width button, **48px height**, **Oxford Blue `#002045` background**, white text, `border-radius: 8px`. Label: "生成题目" (Generate Questions). Add a subtle hover effect (slightly darker).

### Question Card Display Area

Below the button, show **3 sample question cards** in a vertical stack (one column, full width). Each card has:

- **Card container**: white background, `1px solid #e5e5e5`, `border-radius: 8px`, padding `20px`, subtle box-shadow on hover.
- **Title**: bold, larger font (Cormorant Garamond). Examples:
  1. "酸碱中和反应计算"
  2. "氧化还原方程式配平"
  3. "金属活动性顺序实验设计"
- **Content preview**: 2-3 lines of gray body text summarizing the question.
- **Audit badge row**: 4 small badges laid out horizontally at the bottom of the card:

  | Badge Label | Status  | Style                          |
  |-------------|---------|--------------------------------|
  | 系数        | pass    | green bg `#e0f2f1`, text `#004f50`, ✓ |
  | 条件        | pass    | green bg `#e0f2f1`, text `#004f50`, ✓ |
  | 产物        | warning | yellow bg `#fff3cd`, text `#856404`, ⚠ |
  | 结构        | blocked | red bg `#ffdad6`, text `#93000a`, ✗   |

  Vary the badge statuses across the 3 cards so they are not identical. Each badge is a small pill/chip with appropriate background color, text color, and icon.

---

## Tab 2 — 题库管理 (Question Bank Management)

### Layout

A two-column layout: **left sidebar (~240px)** for folder navigation, **right area (flex: 1)** for the question grid.

### Left Sidebar — Folder List

A vertical list of clickable folder items with folder icons:

- 化学 (Chemistry) — selected/active by default
- 物理 (Physics)
- 生物 (Biology)
- 月考 (Monthly Exams)
- 期中期末考试 (Midterm & Final Exams)

Active folder has a light Oxford Blue tint background. Each item shows a folder icon and the name.

### Right Area — Question Grid

A **2-column or 3-column grid** (CSS Grid) of **6 question thumbnail cards**. Each thumbnail card is compact:

- Small card: `border-radius: 8px`, light border, padding `12px`.
- Shows a short question title and a one-line preview.
- Shows a small colored dot or tag indicating the subject (e.g., blue = 化学, green = 物理, purple = 生物).

Use 6 distinct sample questions spread across the 3 subjects.

---

## Tab 3 — 历史真题库 (Past Exam Papers)

### Search & Filter Bar

- A **full-width search input** at the top, placeholder: "搜索真题..." (Search past papers...), with a search icon.
- Below or inline: two `<select>` dropdowns:
  - **地区** (Region): 北京, 上海, 全国卷, 江苏, 浙江
  - **年份** (Year): 2024, 2023, 2022, 2021, 2020

### Exam Paper Cards

**3 cards** stacked vertically, each containing:

- **Region tag**: a small colored pill (e.g., teal `#13696a` background) showing the region name.
- **Year**: displayed prominently.
- **Question count**: e.g., "25道题" (25 questions).
- A subtle right-arrow or "查看详情" link.
- Light card styling consistent with the design system.

Example data:
1. 北京 · 2024 · 28道题
2. 全国卷 · 2023 · 32道题
3. 上海 · 2022 · 24道题

---

## Tab 4 — 考试列表 (Exam List)

### Header

A row with the heading "考试列表" on the left and a **"创建考试" (Create Exam) button** on the right. The button is Oxford Blue `#002045` background, white text, `border-radius: 8px`, with a "+" icon.

### Exam Cards

**3 cards** stacked vertically. Each shows:

- **Exam name** (bold, Cormorant Garamond). Examples:
  1. "高一化学期中考试"
  2. "高二物理月考"
  3. "高三生物模拟测试"
- **Date**: e.g., "2024-11-15"
- **Status badge** (pill-shaped):
  - 进行中 (In Progress) — **blue** background, white text
  - 已结束 (Ended) — **gray** background, dark text
  - 草稿 (Draft) — **orange** background, white text
- Subtle card border and shadow, `border-radius: 8px`.

---

## JavaScript Requirements

- All tab switching must use **vanilla JavaScript** (no framework).
- On page load, Tab 1 is visible; Tabs 2–4 are hidden (`display: none`).
- Clicking a tab label:
  1. Removes the active underline from all tabs.
  2. Adds the active underline to the clicked tab.
  3. Hides all `.tab-panel` divs.
  4. Shows the panel corresponding to the clicked tab.
- The sub-mode toggle inside Tab 1 works the same way (show/hide within Tab 1 context).
- Chip selection toggles the `active` class on click.
- Keep the JS clean and minimal — no library dependencies.

---

## Important Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond and IBM Plex Sans via a `<link>` tag in `<head>`.
- **Icons**: use simple Unicode/HTML entities or inline SVGs — do NOT import icon libraries. For search use 🔍 or an inline SVG magnifying glass. For audit badges use ✓, ⚠, ✗.
- **No images**: everything is text, CSS, and simple shapes.
- **Desktop only**: optimize for 1280px+ viewports.
- The design should feel clean, professional, and academic — like a serious EdTech tool for chemistry/physics/biology teachers.
- Include realistic Chinese text throughout for labels, placeholders, and sample content.
