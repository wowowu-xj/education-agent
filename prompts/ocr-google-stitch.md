# Google Stitch Prompt: Teacher OCR Answer Sheet Grading (ocr.html)

---

Generate a single, self-contained HTML file (`ocr.html`) for a teacher's OCR answer sheet grading page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Table `8px`, Upload zone `8px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `20px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Table dividers**: `1px solid #e0e0e0`
- **Dashed border**: `2px dashed #ccc`
- **Status tag styles**:
  - 已批改 (Graded): green `#e0f2f1` background, text `#004f50`
  - 批改中 (Grading): blue `#e3f2fd` background, text `#1565c0`
  - 等待中 (Waiting): gray `#f5f5f5` background, text `#666`
- **Target viewport**: Desktop 1280px+

The entire page uses `max-width: 1280px`, centered with `margin: 0 auto`, padding `32px`.

---

## Page Layout (Top to Bottom)

### 1. Page Title Bar

A horizontal flexbox row, `align-items: center`, `justify-content: space-between`, `margin-bottom: 24px`:

**Left side:**
- Page heading: "OCR 答题卡批改" (OCR Answer Sheet Grading), Cormorant Garamond, `22px`, bold, Oxford Blue `#002045`

**Right side (flexbox row, `gap: 20px`, `align-items: center`):**

- **"批量上传" (Batch Upload) toggle switch**: a custom CSS toggle switch (checkbox styled as a pill-shaped slider). 
  - Track: `44px` wide, `24px` tall, `border-radius: 12px`, gray `#d5d0c8` when off, Oxford Blue `#002045` when on.
  - Thumb: `20px` white circle, slides left (off) to right (on) with `transition: 0.2s`.
  - Label "批量上传" in `14px` gray text to the left of the toggle.
  - Default state: ON.

- **"历史记录" (History) dropdown**: a `<select>` with options — 最近批改 (Recent Grading, default), 7月月考, 6月月考, 期中考试. Styled: light bg, `1px solid #d5d0c8`, `border-radius: 8px`, `padding: 8px 16px`, `font-size: 14px`, IBM Plex Sans.

---

### 2. Upload Zone

A large drop zone, centered on the page:

- **Dimensions**: `500px` wide, `300px` tall, centered with `margin: 0 auto`
- **Border**: `2px dashed #ccc`, `border-radius: 8px`
- **Background**: `#fafafa`
- **Cursor**: `pointer`
- **Hover state**: border color changes to Oxford Blue `#002045`, background shifts to `#f0f2f5`
- **Transition**: `border-color 0.2s, background-color 0.2s`

Content inside the upload zone (vertically centered using flexbox `flex-direction: column`, `justify-content: center`, `align-items: center`):

1. **Cloud upload icon**: a simple cloud shape built with pure CSS (e.g., a rounded rectangle with overlapping circles using `::before` and `::after` pseudo-elements) OR use the Unicode character ☁️ at `48px` size. Color: gray `#999`.
2. **Prompt text**: "拖拽答题卡图片到此处，或点击选择文件" (Drag answer sheet images here, or click to select files), `14px`, gray `#888`, `margin-top: 16px`.
3. **"选择文件" (Select Files) button**: Oxford Blue `#002045` background, white text, `border-radius: 8px`, `padding: 10px 28px`, `font-size: 14px`, IBM Plex Sans, `margin-top: 16px`. On click, trigger a hidden `<input type="file" accept="image/*" multiple>`.

Below the upload zone, show accepted formats hint: "支持 JPG、PNG、PDF 格式，单文件不超过 10MB" (Supports JPG, PNG, PDF, max 10MB per file), `12px`, gray `#aaa`, centered, `margin-top: 8px`.

---

### 3. Upload Progress Area

A section with the heading "上传进度" (Upload Progress), `16px`, Cormorant Garamond, Oxford Blue, `margin-top: 32px`, `margin-bottom: 12px`.

**3 file status cards** stacked vertically, `8px` gap. Each card is a horizontal flexbox row (`align-items: center`, `padding: 14px 20px`, white background, `border-radius: 8px`, `1px solid #e8e5e0`):

#### Card 1 — "批改完成" (Grading Complete)
- **File icon**: small document icon (📄 or CSS rectangle with folded corner), `24px`, gray
- **File name**: "答题卡_001.jpg", `14px`, bold, Oxford Blue, `margin-left: 12px`
- **Status**: green text "批改完成" (Grading Complete), `13px`, `margin-left: 12px`
- **Green checkmark circle**: `24px` diameter, green `#2e7d32` background, white ✓ inside, `margin-left: 8px`
- **Spacer**: `flex: 1`
- **"查看结果" (View Results) link/button**: Teal `#13696a` text, `13px`, no background, cursor pointer, hover underline. Clicking scrolls down to the results table.

#### Card 2 — "正在识别中..." (Recognizing...)
- **File icon**: 📄 icon, `24px`, gray
- **File name**: "答题卡_002.jpg", `14px`, bold, Oxford Blue, `margin-left: 12px`
- **Status**: blue text "正在识别中..." (Recognizing...), `13px`, `margin-left: 12px`
- **Spinning loader**: a CSS-only spinning circle (`20px` diameter, `2px` solid border with one side transparent, `border-top-color: #3b82f6`, `animation: spin 1s linear infinite`), `margin-left: 8px`
- **Progress bar**: a thin bar (`width: 160px`, `height: 6px`, `border-radius: 8px`, gray `#e0e0e0` track), with a blue `#3b82f6` fill at `65%` width, `margin-left: 16px`
- **Percentage**: "65%", `12px`, gray, `margin-left: 8px`

#### Card 3 — "等待中" (Waiting)
- **File icon**: 📄 icon, `24px`, gray
- **File name**: "答题卡_003.jpg", `14px`, bold, Oxford Blue, `margin-left: 12px`
- **Status**: gray text "等待中" (Waiting), `13px`, `margin-left: 12px`
- **Clock icon**: a simple CSS clock face (`20px` circle with two lines for hands) OR Unicode 🕐, gray `#999`, `margin-left: 8px`
- No progress bar (grayed out or empty)

---

### 4. Grading Results Table

A section with the heading "批改结果" (Grading Results), `16px`, Cormorant Garamond, Oxford Blue, `margin-top: 32px`, `margin-bottom: 12px`.

A full-width table inside a white card wrapper (`border-radius: 8px`, `overflow: hidden`, `1px solid #e8e5e0`):

**Table styles:**
- `width: 100%`, `border-collapse: collapse`
- Table dividers: `border-bottom: 1px solid #e0e0e0` on rows
- Alternating row background: even rows get `#fafafa`, odd rows white
- Row hover: light blue tint `#f5f7fa`
- Cell padding: `12px 16px`, `font-size: 14px`, IBM Plex Sans

**Table header row:**
- Oxford Blue `#002045` background, white text
- `font-size: 13px`, `font-weight: 600`, text-transform uppercase tracking
- Column headers: 姓名 (Name) | 学号 (Student ID) | 总分 (Total Score) | 选择题 (Multiple Choice) | 填空题 (Fill in Blank) | 状态 (Status) | 操作 (Actions)

**5 data rows:**

| # | 姓名 | 学号       | 总分 | 选择题 | 填空题 | 状态   | 操作           |
|---|------|-----------|------|--------|--------|--------|----------------|
| 1 | 张明 | G20240301 | 85   | 45/50  | 40/50  | 已批改 | [详情] [导出]   |
| 2 | 李华 | G20240302 | 72   | 38/50  | 34/50  | 已批改 | [详情] [导出]   |
| 3 | 王芳 | G20240303 | 91   | 48/50  | 43/50  | 已批改 | [详情] [导出]   |
| 4 | 赵磊 | G20240304 | 58   | 32/50  | 26/50  | 批改中 | [详情] [导出]   |
| 5 | 陈静 | G20240305 | 76   | 40/50  | 36/50  | 已批改 | [详情] [导出]   |

**Status column rendering:**
- 已批改 (Graded): small pill tag — green `#e0f2f1` background, `#004f50` text, `border-radius: 16px`, `padding: 3px 12px`, `font-size: 12px`
- 批改中 (Grading): small pill tag — blue `#e3f2fd` background, `#1565c0` text, same sizing

**Actions column:**
- "详情" (Details): small text button, Teal `#13696a` text, `font-size: 12px`, `padding: 4px 10px`, `border-radius: 6px`, no background, cursor pointer, hover: light teal background `#e0f2f1`
- "导出" (Export): small text button, gray `#888` text, `font-size: 12px`, `padding: 4px 10px`, `border-radius: 6px`, no background, cursor pointer, hover: light gray background
- `4px` gap between the two buttons

**Score cells:**
- 总分 (Total Score): Oxford Blue `#002045`, `bold`, `16px`
- 选择题/填空题: gray `13px`, format "得分/满分" (e.g., "45/50")

---

### 5. Bottom Sticky Action Bar

A **sticky footer bar** (`position: sticky`, `bottom: 0`, `z-index: 10`):

- **Background**: `#f5f5f5`
- **Padding**: `16px 24px`
- **Border top**: `1px solid #e0e0e0`
- **Border radius**: `8px` (top corners only)
- **Display**: flexbox row, `align-items: center`, `justify-content: space-between`
- **Margin top**: `32px`

**Left side — Summary stats** (flexbox row, `gap: 32px`):

Three stat items in a row. Each: gray `13px` label on top, Oxford Blue `#002045` `20px` bold number below:

| Label    | Value |
|----------|-------|
| 平均分   | 72.4  |
| 最高分   | 98    |
| 最低分   | 45    |

Use `|` divider (gray `#d5d0c8`) between stat items.

**Right side — Action buttons** (flexbox row, `gap: 8px`):

Three buttons, `border-radius: 8px`, `padding: 10px 20px`, `font-size: 14px`, `font-weight: 500`, IBM Plex Sans, cursor pointer:

1. **"导出成绩" (Export Scores)**: Teal `#13696a` background, white text. Hover: slightly darker teal.
2. **"发送给学生" (Send to Students)**: white background, `1px solid #13696a`, Teal `#13696a` text (outline style). Hover: light teal background.
3. **"开始诊断障碍" (Start Obstacle Diagnosis)**: Oxford Blue `#002045` background, white text. Hover: slightly darker. This is the primary CTA — consider making it slightly wider or adding a subtle arrow icon →.

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### File Upload Interaction:
1. Clicking the upload zone or the "选择文件" button triggers a hidden `<input type="file" accept="image/*" multiple>`.
2. When files are selected (simulated — no actual upload needed):
   - Show a brief visual feedback: the upload zone border briefly flashes Oxford Blue.
   - This is optional / nice-to-have. The progress cards below are already showing simulated states, so the upload zone can remain static.

### Toggle Switch:
1. The "批量上传" toggle switch works: clicking the label or the switch toggles the checkbox state.
2. Update the track background color (gray when off, Oxford Blue when on).

### "查看结果" Link:
1. Clicking "查看结果" on Card 1 smoothly scrolls the page down to the results table section using `Element.scrollIntoView({ behavior: 'smooth' })`.

### Spinning Loader:
1. Pure CSS animation `@keyframes spin { 100% { transform: rotate(360deg); } }` applied to the loader element.

### Sticky Bar Visibility:
- The sticky bar should remain visible when scrolling through the results table. Since it uses `position: sticky; bottom: 0`, this should work naturally.

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond and IBM Plex Sans via a `<link>` in `<head>`.
- **Icons**: use Unicode characters (☁️ cloud, 📄 document, ✓ checkmark, 🕐 clock) or simple CSS shapes. For the spinning loader, use a pure CSS border-circle animation. No icon libraries.
- **No images**: cloud icon, document icons, checkmark, clock are all Unicode or CSS.
- **Upload zone**: the dashed border must be exactly `2px dashed #ccc`. The zone should feel inviting and clearly interactive.
- **Table**: ensure alternating row colors and hover effects are clean. The table wrapper has `overflow: hidden` to clip the border-radius.
- **Sticky bar**: ensure it sits above all other content (z-index) and has a subtle shadow `0 -2px 8px rgba(0,0,0,0.06)` to separate it from the page.
- **Transitions**: use CSS transitions for button hovers, toggle switch, upload zone hover, and status tag appearances.
- **Page background**: use `#faf8f5` behind the main content area so the sticky bar's `#f5f5f5` still contrasts slightly.
- The overall feel should be efficient and workflow-oriented — a practical grading tool that clearly communicates progress and results at a glance.

---

## Visual Structure Summary

```
┌──────────────────────────────────────────────────────────────┐
│  OCR 答题卡批改                  [批量上传 ⬤] [历史记录 ▼]    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│              ┌─────────────────────────────┐                 │
│              │                             │                 │
│              │            ☁️               │                 │
│              │                             │                 │
│              │  拖拽答题卡图片到此处，       │                 │
│              │  或点击选择文件              │                 │
│              │                             │                 │
│              │      [选择文件]              │                 │
│              │                             │                 │
│              └─────────────────────────────┘                 │
│              支持 JPG、PNG、PDF 格式，单文件不超过 10MB        │
├──────────────────────────────────────────────────────────────┤
│  上传进度                                                     │
│  ┌──────────────────────────────────────────────────────────┐
│  │ 📄 答题卡_001.jpg  批改完成  ✓  (green)     [查看结果]    │
│  └──────────────────────────────────────────────────────────┘
│  ┌──────────────────────────────────────────────────────────┐
│  │ 📄 答题卡_002.jpg  正在识别中...  ◌ (spin) ██████░░ 65%  │
│  └──────────────────────────────────────────────────────────┘
│  ┌──────────────────────────────────────────────────────────┐
│  │ 📄 答题卡_003.jpg  等待中  🕐 (gray)                      │
│  └──────────────────────────────────────────────────────────┘
├──────────────────────────────────────────────────────────────┤
│  批改结果                                                     │
│  ┌──────────────────────────────────────────────────────────┐
│  │ 姓名 │ 学号       │ 总分 │ 选择题  │ 填空题  │ 状态  │ 操作   │
│  │──────────────────────────────────────────────────────────│
│  │ 张明 │ G20240301 │ 85   │ 45/50   │ 40/50   │ 已批改 │ 详情 导出│
│  │ 李华 │ G20240302 │ 72   │ 38/50   │ 34/50   │ 已批改 │ 详情 导出│
│  │ 王芳 │ G20240303 │ 91   │ 48/50   │ 43/50   │ 已批改 │ 详情 导出│
│  │ 赵磊 │ G20240304 │ 58   │ 32/50   │ 26/50   │ 批改中 │ 详情 导出│
│  │ 陈静 │ G20240305 │ 76   │ 40/50   │ 36/50   │ 已批改 │ 详情 导出│
│  └──────────────────────────────────────────────────────────┘
├──────────────────────────────────────────────────────────────┤
│  平均分 72.4  |  最高分 98  |  最低分 45                       │
│                    [导出成绩] [发送给学生] [开始诊断障碍]        │
│  ────────────────────────────────────────────────────────    │
│  (sticky bottom bar, #f5f5f5 background)                     │
└──────────────────────────────────────────────────────────────┘
```
