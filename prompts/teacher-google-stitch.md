# Google Stitch Prompt: Teacher Class Analytics Dashboard (teacher.html)

---

Generate a single, self-contained HTML file (`teacher.html`) for a teacher's class learning analytics dashboard. It must use **vanilla HTML + CSS only** — no JavaScript frameworks, no chart libraries (no Chart.js, no ECharts). All charts are built with pure CSS/HTML divs and positioning. All CSS and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `24px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Target viewport**: Desktop 1280px+

---

## Page Layout (Top to Bottom)

The entire page uses `max-width: 1280px`, centered with `margin: 0 auto`, padding `32px`.

### 1. Toolbar

A horizontal bar at the top containing two dropdown selectors side by side with `16px` gap:

- **班级 (Class) dropdown**: a `<select>` with options — 高一(1)班, 高一(2)班, **高一(3)班** (pre-selected/default), 高一(4)班, 高一(5)班
- **时间范围 (Time Range) dropdown**: a `<select>` with options — **本学期** (pre-selected/default), 上学期, 本学年

Each dropdown is styled with: light background, `1px solid #d5d0c8` border, `8px` border-radius, `12px 16px` padding, IBM Plex Sans font. Add a small label above each dropdown in gray `14px` text.

### 2. Row 1 — 4 KPI Overview Cards

A **CSS Grid with 4 equal columns**, `16px` gap. Each KPI card:

- White background, `8px` border-radius, `24px` padding
- **Number**: Oxford Blue `#002045`, `28px`, `bold`, IBM Plex Sans
- **Label**: gray `#888`, `14px`, below the number, `4px` margin-top
- Subtle bottom border accent: `3px` solid, color varies per card:
  - Card 1 (考试次数): Teal `#13696a`
  - Card 2 (关注学生): warm amber `#e6a817`
  - Card 3 (班级平均分): Oxford Blue `#002045`
  - Card 4 (知识点掌握率): green `#2e7d32`

KPI data:

| Label          | Value | Accent Color |
|----------------|-------|--------------|
| 考试次数       | 12    | #13696a      |
| 关注学生       | 5人   | #e6a817      |
| 班级平均分     | 78.5  | #002045      |
| 知识点掌握率   | 73%   | #2e7d32      |

### 3. Row 2 — Two-Column Layout (60% Left / 40% Right)

A flexbox row with `16px` gap.

#### Left Column (60%) — Knowledge Point Error Rate Bar Chart

A card with the heading "知识点错误率" (Knowledge Point Error Rate).

Build a **pure CSS horizontal bar chart** with 6 bars:

- **Y-axis (left)**: percentage labels 0%, 10%, 20%, 30%, 40%, 50% stacked vertically
- **Grid lines**: horizontal dashed or solid lines in `#e8e5e0` behind the bars
- **Bars**: each bar is a `<div>` with Teal `#13696a` background, `6px` border-radius on the right end, height `28px`. Bar width is set via inline `style="width: X%"` based on the error rate
- **X-axis labels (bottom)**: knowledge point names below each bar

Data for the 6 bars (knowledge point → error rate %):

| Knowledge Point    | Error Rate |
|--------------------|-----------|
| 氧化还原           | 42%        |
| 离子反应           | 35%        |
| 化学键             | 28%        |
| 元素周期律         | 38%        |
| 化学平衡           | 45%        |
| 电化学             | 31%        |

Each bar has the percentage number shown at the right tip of the bar in `12px` bold text.

The chart area should have a light `#f5f3ef` background to distinguish it from the card.

#### Right Column (40%) — Obstacle Type Breakdown

A card with the heading "障碍类型分布" (Obstacle Type Distribution).

Display **3 horizontal segmented bars** (each full width of the card), one per obstacle type. Each bar is a horizontal track with:

- A colored segment proportional to the percentage
- A label on the left showing the obstacle type name
- The percentage number on the right

Data:

| Obstacle Type      | Percentage | Color   |
|--------------------|-----------|---------|
| 概念理解障碍       | 30%        | Purple `#7b4fbf` |
| 审题障碍           | 50%        | Blue `#3b82f6`   |
| 表述障碍           | 20%        | Cyan `#0891b2`   |

Each segmented bar: full-width container with `height: 12px`, `border-radius: 6px`, gray `#e8e5e0` background. The filled portion uses the corresponding color, `border-radius: 6px`, width set via inline style.

Below the bars, show 3 legend items in a row: colored dot + label + percentage.

### 4. Row 3 — Full-Width Score Trend Line Chart

A card with the heading "成绩趋势" (Score Trend).

Build a **pure CSS line chart** with two data series:

- **班级平均分 (Class Average)**: Oxford Blue `#002045`, solid line
- **年级平均分 (Grade Average)**: gray `#999`, dashed style

Implementation approach:
- Chart area: relative-positioned container, `height: 280px`, light `#f5f3ef` background
- Y-axis on the left: tick marks at 60, 65, 70, 75, 80, 85, 90 with horizontal grid lines
- X-axis on the bottom: month labels
- Data points: small circles (`width: 10px`, `height: 10px`, `border-radius: 50%`) absolutely positioned by `bottom` and `left` percentages
- Lines between points: thin `<div>` elements rotated via CSS `transform: rotate()` and absolutely positioned to connect adjacent points — OR use an SVG `<polyline>` inside the HTML (inline SVG is acceptable since it's native HTML, not a library)

Data points (6 months: Sep–Feb, next year):

| Month | Class Avg | Grade Avg |
|-------|----------|-----------|
| 9月   | 72       | 70        |
| 10月  | 74       | 71        |
| 11月  | 71       | 72        |
| 12月  | 76       | 73        |
| 1月   | 78       | 74        |
| 2月   | 78.5     | 74.5      |

Y-axis range: 60 to 90. Scale data points proportionally.

Below the chart, include a legend: Oxford Blue dot + "班级平均分", gray dashed line marker + "年级平均分".

### 5. Row 4 — "关注学生" (Students of Concern) Horizontal Scroll List

A card/section with the heading "关注学生" and a subtitle "5人需要特别关注".

A **horizontally scrollable container** (`overflow-x: auto`, `display: flex`, `gap: 16px`) containing **5 student cards**. Each card:

- **Width**: `220px`, fixed (not flex-grow)
- **White background**, `8px` border-radius, `16px` padding, subtle border
- **Avatar placeholder**: `40px` circle, gray `#d5d0c8` background, centered initials in white (e.g., "张", "李", "王", "赵", "陈")
- **Student name**: below avatar, `16px`, Cormorant Garamond, bold
- **Obstacle type tag**: a small pill-shaped badge with background color matching the obstacle type:
  - 概念 = purple `#7b4fbf` bg, white text
  - 审题 = blue `#3b82f6` bg, white text
  - 表述 = cyan `#0891b2` bg, white text
- **Recent score trend bar**: a thin horizontal bar, `height: 6px`, `border-radius: 3px`, showing small Oxford Blue `#002045` segments representing recent test scores. Use 5 tiny squares/dots in a row, filled = passed, hollow = failed — or a simple mini progress bar.
- **Last score**: small gray text showing the most recent score, e.g., "最近: 62分"

Student data:

| Name | Obstacle Type | Recent Scores (5 tests)     | Latest |
|------|--------------|-----------------------------|--------|
| 张明  | 概念         | pass, pass, fail, pass, fail | 62     |
| 李华  | 审题         | pass, fail, fail, pass, pass | 58     |
| 王芳  | 表述         | fail, pass, pass, pass, fail | 55     |
| 赵磊  | 概念         | pass, pass, pass, fail, fail | 60     |
| 陈静  | 审题         | fail, fail, pass, pass, pass | 64     |

For the trend bar: 5 small blocks in a row. Passed = Oxford Blue `#002045` filled block. Failed = light gray `#e8e5e0` block. Each block is `16px` wide, `6px` high, `2px` gap.

The scroll container should have a subtle fade-out hint on the right edge (optional, using a CSS gradient pseudo-element `::after` with `linear-gradient(to right, transparent, #faf8f5)`).

---

## CSS / Implementation Notes

- **No JavaScript at all** — this is a static dashboard. All data is hardcoded sample data. Dropdowns are visual only (no event handlers needed).
- **All charts are pure CSS/HTML** — use `<div>` elements with inline `style` widths, absolute positioning within a `position: relative` container, and CSS shapes. For the line chart, use inline SVG `<svg>` with `<polyline>` inside the HTML file — this is native HTML5, not a library, and is acceptable.
- **Google Fonts**: load Cormorant Garamond and IBM Plex Sans via a `<link>` in `<head>`.
- **Icons/indicators**: use Unicode symbols or simple CSS shapes. No icon libraries.
- **No images**: avatar placeholders are CSS circles with text.
- **Section spacing**: `24px` vertical gap between rows.
- **Section headings**: Cormorant Garamond, `20px`, Oxford Blue `#002045`, with a subtle bottom border or underline accent.
- **Scrollbar styling** (optional): for the horizontal scroll list, use `::-webkit-scrollbar` to make the scrollbar thin and subtle.
- The overall feel should be warm, calm, and data-rich — like a thoughtful analytics dashboard for a dedicated teacher, not a cold corporate BI tool.

---

## Summary of All Rows

```
┌──────────────────────────────────────────────────────┐
│  Toolbar: [班级 ▼] [时间范围 ▼]                       │
├──────────┬──────────┬──────────┬──────────────────────┤
│ 考试次数  │ 关注学生  │ 班级平均分│ 知识点掌握率           │
│   12     │  5人     │  78.5   │  73%                │
├─────────────────────────┬────────────────────────────┤
│  知识点错误率 (60%)      │  障碍类型分布 (40%)          │
│  ▓▓▓▓▓▓▓▓ 氧化还原 42%  │  ████ 概念理解 30%          │
│  ▓▓▓▓▓▓▓  离子反应 35%  │  ██████ 审题障碍 50%        │
│  ▓▓▓▓▓   化学键 28%     │  ███ 表述障碍 20%           │
│  ▓▓▓▓▓▓▓ 元素周期律 38% │                            │
│  ▓▓▓▓▓▓▓▓▓ 化学平衡 45% │                            │
│  ▓▓▓▓▓▓  电化学 31%     │                            │
├─────────────────────────┴────────────────────────────┤
│  成绩趋势 (班级 vs 年级)                               │
│  80 ┤                   ●━━●                         │
│  75 ┤      ●━━●━━●━━●                                 │
│  70 ┤ ●━━●                                            │
│     └───┴───┴───┴───┴───┴───                         │
│      9月 10月 11月 12月 1月 2月                        │
├──────────────────────────────────────────────────────┤
│  关注学生  ← scroll →                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ 张明  │ │ 李华  │ │ 王芳  │ │ 赵磊  │ │ 陈静  │       │
│  │ 概念  │ │ 审题  │ │ 表述  │ │ 概念  │ │ 审题  │       │
│  │ ██░█░ │ │ █░░██ │ │ ░███░ │ │ ███░░ │ │ ░░███ │       │
│  │ 62分  │ │ 58分  │ │ 55分  │ │ 60分  │ │ 64分  │       │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘       │
└──────────────────────────────────────────────────────┘
```
