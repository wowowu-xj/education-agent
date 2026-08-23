# Google Stitch Prompt: Student Review Center (m/review.html)

---

Generate a single, self-contained HTML file (`m/review.html`) for a student mobile spaced-repetition review center page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Pending review**: Orange `#FF6B35`
- **Reviewed today**: Blue `#3B5BA5`
- **Mastered**: Green `#2c6e49`
- **Review level tag colors**:
  - Level 2 (7 days): Orange `#FF6B35` background, white text
  - Level 1 (3 days): Blue `#3B5BA5` background, white text
  - Level 0 (first time): Green `#2c6e49` background, white text
- **Completed card**: `opacity: 0.6`, grayed-out buttons
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Level tags `4px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `12px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Target viewport**: Mobile — `max-width: 390px`, centered with `margin: 0 auto`
- **Body background**: `#e8e5e0` (desktop backdrop)

---

## Page Container

```css
.container {
  max-width: 390px;
  min-height: 100vh;
  margin: 0 auto;
  background: #faf8f5;
  position: relative;
  display: flex;
  flex-direction: column;
}
```

---

## Component 1 — Top Title Bar

`height: 56px`, Oxford Blue `#002045` background, `display: flex`, `align-items: center`, `padding: 0 12px`:

- **Left — Back arrow**: Unicode `←`, white, `20px`, `cursor: pointer`
- **Center — Title**: "复习中心" (Review Center), `16px`, bold, white, IBM Plex Sans, `position: absolute`, `left: 50%`, `transform: translateX(-50%)`

Nothing on the right side — keep it clean.

---

## Component 2 — Statistics Row

A flexbox row with **3 equal-width columns**, `gap: 8px`, `padding: 16px`:

Each stat column is a small card: white background, `border-radius: 8px`, `padding: 12px 8px`, `text-align: center`, `1px solid #e8e5e0`, `flex: 1`.

Inside each column (top to bottom, centered):

- **Small label**: `12px`, gray `#888`, IBM Plex Sans, `margin-bottom: 6px`
- **Large number**: `28px`, bold, IBM Plex Sans
- **Subtle bottom border accent**: `3px` solid, matching the number color, running along the bottom edge of each card (use a pseudo-element `::after` or an inner `<div>` at the bottom)

| Label        | Value | Color            |
|--------------|-------|------------------|
| 待复习       | 8     | Orange #FF6B35   |
| 今日已复习   | 3     | Blue #3B5BA5     |
| 已掌握       | 15    | Green #2c6e49    |

---

## Component 3 — "今日待复习" Section

### Section Header
`padding: 16px 16px 12px`, `display: flex`, `align-items: baseline`, `gap: 8px`:
- **Title**: "今日待复习", `16px`, bold, Oxford Blue `#002045`, Cormorant Garamond
- **Count**: "(8题)", `13px`, gray `#888`, IBM Plex Sans

### Review Question Cards

Scrollable area: `flex: 1`, `overflow-y: auto`, `padding: 0 16px 80px`, `display: flex`, `flex-direction: column`, `gap: 8px`.

Three question cards. Each card: white background, `border-radius: 8px`, `padding: 12px`, `1px solid #e8e5e0`.

#### Card Layout (same structure for all 3):

**Top row** (`display: flex`, `align-items: center`, `gap: 12px`):

- **Circular question number badge**: `32px × 32px` circle (`border-radius: 50%`), gray `#e8e5e0` background, centered number (`14px`, bold, Oxford Blue `#002045`), `flex-shrink: 0`

- **Middle — Question summary**: `flex: 1`, `font-size: 14px`, `color: #333`, IBM Plex Sans, `line-height: 1.4`, `overflow: hidden`, `text-overflow: ellipsis`, `white-space: nowrap` (single line with ellipsis for long text)

- **Right — Review level tag**: `flex-shrink: 0`, `font-size: 11px`, `font-weight: 500`, white text, `border-radius: 4px`, `padding: 3px 8px`, `white-space: nowrap`

**Bottom — Action button** (`margin-top: 10px`):
- Full width, `height: 36px`, Oxford Blue `#002045` background, white text
- `border-radius: 8px`, `border: none`, `font-size: 13px`, `font-weight: 500`, `cursor: pointer`
- Text: "开始复习" (Start Review)
- Hover: `background: #003060`
- `transition: background 0.15s`

#### Card 1 — Level 2, 7-day review
- **Badge number**: "1"
- **Summary**: "氧化还原反应电子转移计算与化合价变化分析" (14px, #333)
- **Level tag**: "Level 2 · 7天后" — Orange `#FF6B35` background, white text
- **Button**: "开始复习" (Oxford Blue)

#### Card 2 — Level 1, 3-day review
- **Badge number**: "2"
- **Summary**: "离子方程式配平练习与沉淀判断"
- **Level tag**: "Level 1 · 3天后" — Blue `#3B5BA5` background, white text
- **Button**: "开始复习"

#### Card 3 — Level 0, first-time learning
- **Badge number**: "3"
- **Summary**: "化学键类型判断基础与分子结构"
- **Level tag**: "Level 0 · 首次学习" — Green `#2c6e49` background, white text
- **Button**: "开始复习"

---

## Component 4 — "今日已完成" Section

### Section Header
`padding: 16px 16px 12px`, `display: flex`, `align-items: baseline`, `gap: 8px`:
- **Green checkmark**: `✓` (Unicode), Green `#2c6e49`, `16px`, bold
- **Title**: "今日已完成", `14px`, bold, Green `#2c6e49`, Cormorant Garamond
- **Count**: "(3题)", `12px`, gray `#888`, IBM Plex Sans

### Completed Cards

**Card 1** — `margin: 0 16px 12px`, white background, `border-radius: 8px`, `padding: 12px`, `1px solid #e8e5e0`, **`opacity: 0.6`**:

**Top row** (`display: flex`, `align-items: center`, `gap: 12px`):

- **Green checkmark circle**: `32px × 32px` circle (`border-radius: 50%`), Green `#2c6e49` background, white `✓` checkmark inside (`16px`, bold), `flex-shrink: 0`

- **Middle — Title**: `flex: 1`, `font-size: 14px`, `color: #333`, IBM Plex Sans
  - "氧化还原基础练习 — 已完成"

- **Right — Status text**: "已掌握" (Mastered), `13px`, Green `#2c6e49`, `font-weight: 500`, `flex-shrink: 0`

**Bottom — Grayed-out button** (`margin-top: 10px`):
- Full width, `height: 36px`, gray `#e0e0e0` background, gray `#999` text
- `border-radius: 8px`, `border: none`, `font-size: 13px`, `cursor: default`, `pointer-events: none`
- Text: "已完成" (Completed)
- This contrasts with the active "开始复习" button on pending cards

**Card 2 & 3** — More compact (same `opacity: 0.6`, no bottom button):
- Top row only: ✓ green circle + "离子反应方程式 — 已完成" + "已掌握"
- Top row only: ✓ green circle + "化学平衡判断 — 已完成" + "已掌握"
- `padding: 10px 12px`, `margin: 0 16px 6px`

---

## JavaScript Requirements

Minimal vanilla JS — no frameworks, no libraries.

### Button Click Feedback (cosmetic):
- Clicking "开始复习" on any pending card: briefly change button text to "加载中..." for `0.6s`, then restore. This gives a sense of interactivity without needing actual navigation.
- Clicking a completed card's button: no action (already `pointer-events: none`).

### Bottom Tab Bar:
- "错题" tab is active (Oxford Blue `#002045` icon + text). The review center shares the same navigation slot as the wrong-answer notebook.
- Other tabs inactive (gray `#999`).
- Clicking other tabs updates visual state only.

---

## Common — Bottom 4-Tab Navigation Bar

`position: fixed` (within container), `bottom: 0`, `width: 100%` (max 390px), `height: 56px`, `background: white`, `border-top: 1px solid #eee`, `display: flex`, `justify-content: space-around`, `align-items: center`, `z-index: 50`, `padding-bottom: env(safe-area-inset-bottom, 0)`.

4 tabs (flex: 1, centered column, cursor pointer):

| Tab   | Icon | Label | State    |
|-------|------|-------|----------|
| AI助教 | 💬  | AI助教 | Inactive (gray #999) |
| 练习   | 📝  | 练习   | Inactive (gray #999) |
| 错题   | ❌  | 错题   | **Active** (Oxford Blue #002045) |
| 我的   | 👤  | 我的   | Inactive (gray #999) |

Each tab: icon `20px`, label `10px` with `4px` margin-top.

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond (400, 700) and IBM Plex Sans (400, 500) via a `<link>` in `<head>`.
- **Global box-sizing**: `border-box`.
- **Body styling**: `margin: 0`, `padding: 0`, `background: #e8e5e0`.
- **Container**: `max-width: 390px`, `margin: 0 auto`, `min-height: 100vh`, `background: #faf8f5`, `position: relative`, `display: flex`, `flex-direction: column`, `box-shadow: 0 0 20px rgba(0,0,0,0.05)`.
- **Icons**: Unicode characters only (← back, ✓ checkmark, numbers for badges, 💬📝❌👤 for tabs). No icon libraries.
- **No images**: all visuals are CSS circles, text, colored divs.
- **Level tag colors**: Orange (#FF6B35) / Blue (#3B5BA5) / Green (#2c6e49) — each visually communicates review urgency at a glance. Level 2 = needs most attention (orange = warning), Level 1 = moderate (blue = calm), Level 0 = new/fresh (green = go).
- **Completed contrast**: the `opacity: 0.6` and grayed-out buttons on completed cards create a clear visual distinction between "needs action" and "done". The green checkmark circle reinforces the sense of accomplishment.
- **Stat cards**: the colored bottom accents on each stat card tie the number to its semantic meaning (orange = pending/warning, blue = in progress, green = success).
- **Scrollable content**: the review list area uses `flex: 1` and `overflow-y: auto` with `padding-bottom: 80px` to clear the tab bar.
- **Smooth transitions**: button hovers, stat card hover (subtle lift or shadow).
- **Mobile feel**: the page should feel like a focused study dashboard — spaced-repetition levels are clear, pending vs. completed items are visually distinct, and the overall tone is encouraging ("you're making progress" rather than "you have 8 things to do").

---

## Visual Structure Summary

```
┌──────────────────────────────────────┐
│  ←         复习中心                   │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ 待复习   │ │今日已复习│ │ 已掌握   ││ ← Stats row
│  │   8     │ │   3     │ │   15    ││
│  │ ████████ │ │ ████████ │ │ ████████ ││   Colored bottom accents
│  └─────────┘ └─────────┘ └─────────┘│
├──────────────────────────────────────┤
│  今日待复习 (8题)                     │ ← Section header
│                                      │
│  ┌──────────────────────────────┐    │
│  │ (1) 氧化还原反应电子转移...  │    │ ← Card 1 (Level 2, orange)
│  │                [Level 2·7天后]│    │
│  │ ┌──────────────────────────┐ │    │
│  │ │       开始复习            │ │    │ ← Oxford Blue button
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ (2) 离子方程式配平练习...    │    │ ← Card 2 (Level 1, blue)
│  │                [Level 1·3天后]│    │
│  │ ┌──────────────────────────┐ │    │
│  │ │       开始复习            │ │    │
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ (3) 化学键类型判断基础...    │    │ ← Card 3 (Level 0, green)
│  │                [Level 0·首次学习]│   │
│  │ ┌──────────────────────────┐ │    │
│  │ │       开始复习            │ │    │
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
│                                      │
│  ✓ 今日已完成 (3题)                   │ ← Section header (green)
│                                      │
│  ┌──────────────────────────────┐    │
│  │ (✓) 氧化还原基础练习   已掌握 │    │ ← Completed card
│  │ ┌──────────────────────────┐ │    │   (opacity: 0.6)
│  │ │       已完成              │ │    │ ← Grayed-out button
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ (✓) 离子反应方程式     已掌握 │    │ ← Compact completed
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ (✓) 化学平衡判断       已掌握 │    │ ← Compact completed
│  └──────────────────────────────┘    │
│                                      │
├──────────────────────────────────────┤
│   💬       📝       ❌       👤       │ ← Tab bar (56px)
│  AI助教    练习     错题     我的      │   "错题" active
└──────────────────────────────────────┘
```
