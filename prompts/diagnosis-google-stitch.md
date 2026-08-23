# Google Stitch Prompt: Teacher Obstacle Diagnosis (diagnosis.html)

---

Generate a single, self-contained HTML file (`diagnosis.html`) for a teacher's obstacle diagnosis page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: not used on this page (obstacle colors replace it)
- **Obstacle type colors**:
  - 概念理解型 (Concept): Purple `#7B2D8E`
  - 审题障碍型 (Exam Reading): Blue `#3B5BA5`
  - 表述障碍型 (Expression): Cyan `#00897B`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Chips/tags `16px`, Progress bars `8px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `20px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Confidence progress bar**: `height: 6px`, gray `#e0e0e0` background track, Oxford Blue `#002045` fill, `border-radius: 8px`
- **Target viewport**: Desktop 1280px+

The entire page uses `max-width: 1280px`, centered with `margin: 0 auto`, padding `32px`.

---

## Page Layout (Top to Bottom)

### 1. Toolbar

A horizontal flexbox row inside a white card (`padding: 16px 20px`), with items aligned center, `gap: 16px`:

- **班级 (Class) dropdown**: `<select>` with options — 高一(1)班, 高一(2)班, **高一(3)班** (pre-selected), 高一(4)班, 高一(5)班. Styled: light bg, `1px solid #d5d0c8`, `border-radius: 8px`, `padding: 10px 16px`, IBM Plex Sans.
- **考试 (Exam) dropdown**: `<select>` with options — **7月月考** (pre-selected), 6月月考, 期中考试, 期末考试, 模拟测试. Same styling as class dropdown.
- **"开始诊断" (Start Diagnosis) button**: Oxford Blue `#002045` background, white text, `border-radius: 8px`, `padding: 10px 28px`, `font-size: 14px`, `font-weight: 600`, IBM Plex Sans. Subtle hover darken effect. Pushed to the right side of the toolbar (use `margin-left: auto` or flexbox `justify-content`).

Add small gray `12px` labels above each dropdown.

---

### 2. Two-Column Layout (Left 40% / Right 60%)

A flexbox row with `16px` gap, `margin-top: 24px`.

#### Left Column (40%) — Obstacle Distribution Donut / Ring Chart

A card with the heading "障碍类型分布" (Obstacle Type Distribution), `18px`, Cormorant Garamond, Oxford Blue, centered.

**Option A (preferred — pure CSS donut using conic-gradient):**
- A circular ring chart, `220px` diameter, created with a single `<div>` using `background: conic-gradient(...)`, `border-radius: 50%`, with a white inner circle (`100px` diameter) creating the donut hole, absolutely centered.
- The inner hole displays: "42" (total students) in Oxford Blue `28px` bold, with "总人数" in gray `12px` below it.
- `conic-gradient` segments:
  - Purple `#7B2D8E` from 0° to 108° (30% = 108°)
  - Blue `#3B5BA5` from 108° to 288° (50% = 180°)
  - Cyan `#00897B` from 288° to 360° (20% = 72°)

**Option B (fallback — simpler, more reliable):**
- Three horizontal stacked bar segments inside a card. Each bar: full-width track (`height: 14px`, `border-radius: 7px`, gray `#e8e5e0` background), with a colored fill segment proportional to percentage. Label on left, percentage on right.
  - 概念理解型: 30% — Purple `#7B2D8E`
  - 审题障碍型: 50% — Blue `#3B5BA5`
  - 表述障碍型: 20% — Cyan `#00897B`

Below the chart (either option), show 3 legend items in a horizontal row: colored `10px` circle + obstacle type name + percentage.

#### Right Column (60%) — Summary Stat Cards

Heading "诊断概览" (Diagnosis Overview), `18px`, Cormorant Garamond, Oxford Blue.

Below the heading, **3 small stat cards** in a horizontal flexbox row, equal width (`flex: 1`), `12px` gap. Each card:

- White background, `8px` border-radius, `16px` padding
- **Colored left-border accent**: `3px` left border in the corresponding obstacle color
- **Obstacle type label**: `13px`, colored text matching the obstacle color, IBM Plex Sans, medium weight. e.g., "概念理解型"
- **Student count**: Oxford Blue `#002045`, `28px`, bold, IBM Plex Sans, e.g., "12人"
- **Percentage**: gray `14px` below the count, e.g., "占 28.6%"

Data:

| Obstacle Type  | Count | Percentage | Color     |
|----------------|-------|------------|-----------|
| 概念理解型     | 12人  | 28.6%      | #7B2D8E   |
| 审题障碍型     | 21人  | 50.0%      | #3B5BA5   |
| 表述障碍型     | 9人   | 21.4%      | #00897B   |

---

### 3. Accordion Sections — "按障碍类型分组" (Grouped by Obstacle Type)

Section heading "按障碍类型分组", `20px`, Cormorant Garamond, Oxford Blue, `margin-top: 32px`, `margin-bottom: 12px`.

Three accordion sections, `8px` gap between them. Each accordion is a white card with `border-radius: 8px`, `1px solid #e8e5e0`.

#### Accordion Header (clickable, toggles the body):

Flexbox row, `padding: 16px 20px`, `cursor: pointer`, user-select none:

- **Colored obstacle tag pill**: small pill (`padding: 4px 14px`, `border-radius: 16px`, `font-size: 13px`, `font-weight: 600`):
  - Section 1: 概念理解型 — Purple `#7B2D8E` background, white text
  - Section 2: 审题障碍型 — Blue `#3B5BA5` background, white text
  - Section 3: 表述障碍型 — Cyan `#00897B` background, white text
- **Student count**: gray `14px` text, e.g., "12人"
- **Expand/collapse arrow** on the far right: Unicode ▼ (down) when collapsed, ▲ (up) when expanded. `transition: transform 0.3s ease`.

#### Accordion Body (collapsible content):

- Use `max-height` transition for smooth expand/collapse: collapsed = `max-height: 0`, expanded = `max-height: 600px` (enough to fit content), `overflow: hidden`, `transition: max-height 0.35s ease`.
- Content area: `padding: 0 20px 20px 20px`.

Inside each accordion body, a **student list table/rows**. Each row (`padding: 12px 0`, bottom border `1px solid #f0ede8`):

1. **Student name**: `15px`, bold, Oxford Blue, Cormorant Garamond. Width ~80px.
2. **Confidence progress bar**: flex-grow area. A thin bar: gray `#e0e0e0` track (`height: 6px`, `border-radius: 8px`, `flex: 1`), with an Oxford Blue `#002045` fill segment (`height: 100%`, `border-radius: 8px`, width set via inline style). Percentage number in `12px` gray text to the right of the bar (e.g., "85%"). Width ~200px.
3. **Weak knowledge point tags**: 3-4 small chips (`padding: 2px 10px`, `font-size: 11px`, `border-radius: 16px`, `background: #f5f3ef`, color: `#666`). Wrapped in a flexbox row with `4px` gap.
4. **"详情" (Details) button**: small text button, Teal-like color `#00897B`, `font-size: 12px`, `padding: 4px 12px`, `border-radius: 8px`, `1px solid #00897B`, white background. Hover: `#00897B` background, white text.

#### Section 1 — 概念理解型 (Purple, 12人) — **Expanded by default**

Show 3 student rows:

| Name | Confidence | Weak Knowledge Points                          |
|------|-----------|------------------------------------------------|
| 张明 | 85%       | 氧化还原, 离子反应, 化学键, 元素周期            |
| 李华 | 72%       | 化学平衡, 电化学, 反应速率                       |
| 赵磊 | 68%       | 离子反应, 化学键, 晶体结构                       |

#### Section 2 — 审题障碍型 (Blue, 21人) — **Collapsed by default**

Show 3 student rows (hidden until expanded):

| Name | Confidence | Weak Knowledge Points                          |
|------|-----------|------------------------------------------------|
| 王芳 | 91%       | 化学平衡, 电离平衡                               |
| 陈静 | 78%       | 氧化还原, 电化学, 离子反应                       |
| 刘洋 | 65%       | 化学键, 分子结构, 晶体结构, 元素周期              |

#### Section 3 — 表述障碍型 (Cyan, 9人) — **Collapsed by default**

Show 2 student rows (hidden until expanded):

| Name | Confidence | Weak Knowledge Points                          |
|------|-----------|------------------------------------------------|
| 周强 | 88%       | 离子反应, 化学平衡                               |
| 吴敏 | 74%       | 氧化还原, 电化学                                 |

---

### 4. Bottom Panel — "已生成的学习计划" (Generated Study Plans)

A collapsible panel at the bottom of the page, `margin-top: 32px`.

**Panel header** (clickable to toggle): gray `#f5f5f5` background, `border-radius: 8px 8px 0 0`, `padding: 16px 20px`, flexbox row:
- Section title "已生成的学习计划", `16px`, Cormorant Garamond, Oxford Blue, bold
- Subtitle: gray `13px`, e.g., "8个计划"
- Expand/collapse arrow ▼/▲ on the right (same pattern as accordion)

**Panel body**: gray `#f5f5f5` background, `border-radius: 0 0 8px 8px`, `padding: 16px 20px`, collapsible with `max-height` transition. **Expanded by default**.

Inside: a simple **table or list** with 5 rows. Each row:

- **Student name**: `14px`, bold, Oxford Blue
- **Plan status tag** (pill, `border-radius: 16px`, `padding: 2px 12px`, `font-size: 12px`):
  - 已生成 (Generated): green `#e0f2f1` background, text `#004f50`
  - 生成中 (Generating): blue `#e3f2fd` background, text `#1565c0`
- **Date**: gray `12px` text, e.g., "2024-07-15"

Data:

| Name | Status   | Date       |
|------|----------|------------|
| 张明 | 已生成   | 2024-07-15 |
| 李华 | 已生成   | 2024-07-15 |
| 王芳 | 已生成   | 2024-07-14 |
| 赵磊 | 生成中   | 2024-07-16 |
| 陈静 | 已生成   | 2024-07-15 |
| 刘洋 | 生成中   | 2024-07-16 |
| 周强 | 已生成   | 2024-07-14 |
| 吴敏 | 生成中   | 2024-07-16 |

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### Accordion Behavior:
1. Each accordion header has a click event listener.
2. Clicking the header toggles the corresponding body:
   - If collapsed → expand: set `max-height` to a value large enough to show content (e.g., `600px`), rotate arrow to ▲.
   - If expanded → collapse: set `max-height` to `0`, rotate arrow to ▼.
3. Only one accordion section is expanded at a time? No — allow multiple sections to be open simultaneously (simpler and more flexible for the user). Each section toggles independently.

### Study Plan Panel Toggle:
1. Clicking the panel header toggles the body open/closed with the same `max-height` transition pattern and arrow rotation.

### Dropdown Interaction (optional):
- The dropdowns and "开始诊断" button are visual only. No actual data loading is needed. However, add a subtle visual feedback when clicking "开始诊断" — e.g., briefly change the button text to "诊断中..." for 1 second, then restore, to give a sense of interactivity. This is a nice-to-have touch.

### Progress Bar Animation (optional nice-to-have):
- When the page loads, confidence progress bars animate from `width: 0` to their target width over `0.6s` with `ease-out`. This can be done by starting them at `width: 0` in CSS and using a short `setTimeout` in JS to set the actual widths, leveraging `transition: width 0.6s ease-out`.

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond and IBM Plex Sans via a `<link>` in `<head>`.
- **Icons**: use Unicode symbols (▼/▲ for accordion arrows, ✓ for generated status, ⟳ for generating). No icon libraries.
- **No images**: all visuals are CSS shapes, text, and colored divs.
- **Page heading**: "障碍诊断" (Obstacle Diagnosis) at the very top, Cormorant Garamond, `28px`, bold, Oxford Blue `#002045`, with a subtitle "高一(3)班 · 7月月考" in gray `14px` below it.
- **Section spacing**: `24px` vertical gap between major sections.
- **Smooth transitions**: use CSS `transition` for accordion `max-height`, arrow rotation, progress bar widths, button hovers, and panel toggle.
- **Color consistency**: obstacle colors (purple/blue/cyan) must be used consistently across the donut chart, stat cards, accordion tags, and any obstacle references throughout the page.
- The overall feel should be analytical and structured — a diagnostic tool that helps teachers quickly identify student obstacle patterns and drill down into individual cases.

---

## Visual Structure Summary

```
┌──────────────────────────────────────────────────────────────┐
│  障碍诊断                                                     │
│  高一(3)班 · 7月月考                                          │
├──────────────────────────────────────────────────────────────┤
│  [班级: 高一(3)班 ▼]  [考试: 7月月考 ▼]       [开始诊断]       │
├────────────────────────┬─────────────────────────────────────┤
│  障碍类型分布 (40%)     │  诊断概览 (60%)                      │
│                        │  ┌──────────┐ ┌──────────┐ ┌──────────┐
│      ┌──────┐          │  │ 概念理解型 │ │ 审题障碍型 │ │ 表述障碍型 │
│      │  ◐   │          │  │  12人     │ │  21人     │ │  9人      │
│      │ 42   │          │  │  28.6%    │ │  50.0%    │ │  21.4%    │
│      │ 总人数│          │  └──────────┘ └──────────┘ └──────────┘
│      └──────┘          │
│  ● 概念  ■ 审题  ▲ 表述│
├────────────────────────┴─────────────────────────────────────┤
│  按障碍类型分组                                               │
│  ┌──────────────────────────────────────────────────────────┐
│  │ [概念理解型] 12人                                    ▲    │
│  │──────────────────────────────────────────────────────────│
│  │ 张明  ████████████░ 85%  [氧化还原] [离子反应] [化学键] [详情] │
│  │ 李华  ██████████░░░ 72%  [化学平衡] [电化学] [反应速率]  [详情] │
│  │ 赵磊  █████████░░░░ 68%  [离子反应] [化学键] [晶体结构]   [详情] │
│  └──────────────────────────────────────────────────────────┘
│  ┌──────────────────────────────────────────────────────────┐
│  │ [审题障碍型] 21人                                    ▼    │
│  └──────────────────────────────────────────────────────────┘
│  ┌──────────────────────────────────────────────────────────┐
│  │ [表述障碍型] 9人                                     ▼    │
│  └──────────────────────────────────────────────────────────┘
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐
│  │ 已生成的学习计划 8个计划                                ▲  │
│  │──────────────────────────────────────────────────────────│
│  │ 张明  [已生成] 2024-07-15   赵磊  [生成中] 2024-07-16       │
│  │ 李华  [已生成] 2024-07-15   陈静  [已生成] 2024-07-15       │
│  │ 王芳  [已生成] 2024-07-14   刘洋  [生成中] 2024-07-16       │
│  │ 周强  [已生成] 2024-07-14   吴敏  [生成中] 2024-07-16       │
│  └──────────────────────────────────────────────────────────┘
└──────────────────────────────────────────────────────────────┘
```
