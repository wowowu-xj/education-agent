# Google Stitch Prompt: Student Wrong Answer Notebook (m/wrong.html)

---

Generate a single, self-contained HTML file (`m/wrong.html`) for a student mobile wrong-answer notebook page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Mastered green**: `#2c6e49`
- **Obstacle type tag colors**:
  - 概念理解型 (Concept): Purple `#7B2D8E` background, white text
  - 审题障碍型 (Exam Reading): Blue `#3B5BA5` background, white text
  - 表述障碍型 (Expression): Cyan `#00897B` background, white text
- **Wrong answer**: red background `#fff0f0`, text `#c0392b`
- **Correct answer**: green background `#f0fff0`, text `#2c6e49`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Obstacle tags `4px`, Answer blocks `4px`
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
- **Center — Title**: "错题本" (Wrong Answer Notebook), `16px`, bold, white, IBM Plex Sans, `position: absolute`, `left: 50%`, `transform: translateX(-50%)`
- **Right — Filter icon**: a simple funnel shape built with CSS (a trapezoid/triangle using borders, or use Unicode `⫶` or a vertical filter icon made of 3 horizontal lines of decreasing width) OR use the Unicode character `☰` rotated. Simplest: use `▼` or build a tiny CSS funnel. `20px`, white, `cursor: pointer`, `margin-left: auto`

---

## Component 2 — Statistics Cards Row

A flexbox row with **3 equal-width columns**, `gap: 8px`, `padding: 16px`, `margin-top: 0`:

Each stat column is a small card: white background, `border-radius: 8px`, `padding: 12px 8px`, `text-align: center`, `1px solid #e8e5e0`, `flex: 1`.

Inside each column (top to bottom, centered):

- **Small label**: `12px`, gray `#888`, IBM Plex Sans, `margin-bottom: 6px`
- **Large number**: `28px`, bold, IBM Plex Sans

| Label      | Value | Number Color       |
|------------|-------|--------------------|
| 总错题     | 23    | Oxford Blue #002045 |
| 本周新增   | 5     | Oxford Blue #002045 |
| 已掌握     | 12    | Green #2c6e49       |

---

## Component 3 — Wrong Answer List

A scrollable area: `flex: 1`, `overflow-y: auto`, `padding: 0 16px 80px` (extra bottom padding for the tab bar), `display: flex`, `flex-direction: column`, `gap: 8px`.

Three wrong-answer cards. Each card uses JavaScript accordion behavior: clicking the header toggles the body content with a `max-height` transition.

---

### Card 1 — **Expanded by default** (概念理解型, Concept)

#### Card Header (clickable toggle)
`display: flex`, `align-items: center`, `justify-content: space-between`, `padding: 0` (card already has padding), `cursor: pointer`, `user-select: none`:

- **Left section** (`display: flex`, `align-items: center`, `gap: 10px`):
  - **Question number**: "#1", `14px`, bold, Oxford Blue `#002045`
  - **Obstacle tag**: "概念理解型", `11px`, white text, Purple `#7B2D8E` background, `border-radius: 4px`, `padding: 2px 8px`, `font-weight: 500`

- **Right — Expand/collapse arrow**: Unicode `▼` (down = expanded), `12px`, gray `#999`, `transition: transform 0.3s ease`. When expanded: `transform: rotate(180deg)` (points up).

#### Card Body (expanded — max-height large enough to fit content, e.g., `500px`)
`overflow: hidden`, `transition: max-height 0.3s ease`. Content: `padding-top: 12px`.

**Full question text:**
- `font-size: 14px`, `color: #333`, `line-height: 1.6`, IBM Plex Sans, `margin-bottom: 10px`
- Text: "下列物质中，属于电解质的是？A. 蔗糖 B. NaCl溶液 C. 熔融NaOH D. 铜"

**Wrong answer block:**
- `background: #fff0f0`, `border-radius: 4px`, `padding: 8px 12px`, `margin-bottom: 8px`
- `font-size: 13px`, `display: flex`, `align-items: center`, `gap: 6px`
- Red `✗` icon or bold red label "你的答案：" (Your answer:), color `#c0392b`
- Answer text: "B", `font-weight: 500`, color `#c0392b`

**Correct answer block:**
- `background: #f0fff0`, `border-radius: 4px`, `padding: 8px 12px`, `margin-bottom: 10px`
- `font-size: 13px`, `display: flex`, `align-items: center`, `gap: 6px`
- Green `✓` icon or bold green label "正确答案：" (Correct answer:), color `#2c6e49`
- Answer text: "C", `font-weight: 500`, color `#2c6e49`

**Explanation text:**
- `font-size: 13px`, `color: #666`, `line-height: 1.6`, IBM Plex Sans, `margin-bottom: 12px`
- Text: "电解质定义：在水溶液或熔融状态下能导电的化合物。蔗糖是非电解质，NaCl溶液是混合物不是化合物，铜是金属单质。熔融NaOH是化合物且在熔融状态下能导电，属于电解质。"

**Bottom action buttons** (`display: flex`, `gap: 8px`):

- **"生成变式题" (Generate Variant Question)**:
  - `flex: 1`, `height: 40px`
  - Teal `#13696a` background, white text
  - `border-radius: 8px`, `border: none`, `font-size: 13px`, `font-weight: 500`, `cursor: pointer`
  - Hover: slightly darker teal

- **"已掌握" (Mastered)**:
  - `flex: 1`, `height: 40px`
  - Oxford Blue `#002045` background, white text
  - `border-radius: 8px`, `border: none`, `font-size: 13px`, `font-weight: 500`, `cursor: pointer`
  - Hover: `#003060`

---

### Card 2 — **Collapsed by default** (审题障碍型, Exam Reading)

#### Card Header (clickable toggle)
Same structure as Card 1 header:

- **Left**: "#2" (14px bold Oxford Blue) + "审题障碍型" tag (11px white, Blue `#3B5BA5` bg, `border-radius: 4px`, `padding: 2px 8px`)
- **Right**: `▶` or `›` arrow (right-pointing = collapsed), `12px`, gray `#999`. When expanded: `transform: rotate(90deg)` (points down).

#### One-line Question Summary (visible when collapsed)
`font-size: 13px`, `color: #999`, IBM Plex Sans, `white-space: nowrap`, `overflow: hidden`, `text-overflow: ellipsis`, `margin-top: 6px`, `padding-left: 0`:
- "关于化学键类型的判断，下列说法正确的是..."

#### Card Body (collapsed — `max-height: 0`, expands on click to `max-height: 500px`)
Same structure as Card 1 body when expanded:

- Full question: "关于化学键类型的判断，下列说法正确的是？A. HCl中只含离子键 B. NaOH中只含离子键 C. NH₄Cl中既含离子键又含共价键 D. H₂O中只含离子键"
- Wrong answer: 你的答案：A (red block)
- Correct answer: 正确答案：C (green block)
- Explanation: "离子键存在于活泼金属与活泼非金属之间（或铵盐中），共价键存在于非金属原子之间。NaOH中Na⁺与OH⁻之间是离子键，O与H之间是共价键。NH₄Cl中NH₄⁺与Cl⁻之间是离子键，N与H之间是共价键。"
- Action buttons: "生成变式题" + "已掌握"

---

### Card 3 — **Collapsed by default** (表述障碍型, Expression)

#### Card Header
- **Left**: "#3" (14px bold Oxford Blue) + "表述障碍型" tag (11px white, Cyan `#00897B` bg, `border-radius: 4px`, `padding: 2px 8px`)
- **Right**: `▶` arrow (collapsed)

#### One-line Question Summary (collapsed)
- "用化学方程式表示下列物质的制备方法..."

#### Card Body (collapsed — `max-height: 0`)
When expanded:

- Full question: "用化学方程式表示下列物质的制备方法，并注明反应类型：(1) 实验室制取氯气 (2) 工业制取硫酸的第一步反应"
- Wrong answer: 你的答案：MnO₂ + 2HCl = MnCl₂ + H₂O（未配平，缺少加热条件）(red block)
- Correct answer: MnO₂ + 4HCl(浓) ≜ MnCl₂ + Cl₂↑ + 2H₂O (green block)
- Explanation: "实验室制取氯气需要使用浓盐酸并在加热条件下进行，方程式必须配平且标注反应条件（加热≜）、气体符号↑。反应物HCl需标注'浓'。这是典型的氧化还原反应。"
- Action buttons: "生成变式题" + "已掌握"

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### Accordion Behavior:
1. Each card header has a click event listener.
2. Clicking a header toggles THAT card's body only (independent accordions — multiple can be open simultaneously):
   - If collapsed → expand: set `max-height` to `500px` (enough to fit content), rotate arrow (▼ rotated 180° for Card 1; ▶ rotated 90° for Cards 2/3).
   - If expanded → collapse: set `max-height` to `0`, restore arrow rotation.
3. Use CSS `transition: max-height 0.3s ease` for smooth animation.
4. The one-line question summary (visible when collapsed) is *always* in the DOM but naturally hidden when the body is expanded (it sits between the header and the body, so it slides up under the header as the body expands).

### Button Clicks (cosmetic feedback):
- "生成变式题": show a brief visual feedback (button text changes to "生成中..." for 0.8s, then restores).
- "已掌握": toggle the button appearance — change text to "✓ 已掌握", change background to green `#2c6e49`, disable pointer events. This gives a satisfying "mastered" interaction.

### Bottom Tab Bar:
- "错题" tab is active (Oxford Blue `#002045` icon + text). Other tabs inactive (gray `#999`). Clicking other tabs updates visual state only.

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
- **Icons**: Unicode characters only (← back, ▼/▶ accordion arrows, ✗/✓ for answer blocks, funnel for filter can be a simple CSS trapezoid or Unicode `⫶`). No icon libraries.
- **No images**: all visuals are CSS shapes, text, colored divs.
- **Card accordion**: use `max-height` transition (not `height: auto`) for smooth expand/collapse. Set `overflow: hidden` on the body container.
- **Color-coded answer blocks**: the red (`#fff0f0`) and green (`#f0fff0`) backgrounds provide immediate visual contrast between wrong and correct answers.
- **Obstacle tags**: distinct colors (purple/blue/cyan) make it easy to scan and identify error types at a glance.
- **Smooth transitions**: accordion max-height 0.3s, arrow rotation 0.3s, button hovers.
- **Mobile feel**: the page should feel like a focused study tool — clean, organized, with clear feedback on what was wrong and why. The expand/collapse interaction lets students self-test: read the question collapsed, try to answer mentally, then expand to check.

---

## Visual Structure Summary

```
┌──────────────────────────────────────┐
│  ←         错题本            ⫶       │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ 总错题   │ │ 本周新增 │ │ 已掌握   ││ ← Stats row (3 cols)
│  │   23    │ │    5    │ │   12    ││
│  └─────────┘ └─────────┘ └─────────┘│
├──────────────────────────────────────┤
│  ┌──────────────────────────────┐    │
│  │ #1 [概念理解型]            ▼  │    │ ← Card 1 header (expanded)
│  │──────────────────────────────│    │
│  │ 下列物质中，属于电解质       │    │
│  │ 的是？A.蔗糖 B.NaCl溶液      │    │ ← Full question
│  │ C.熔融NaOH D.铜              │    │
│  │                              │    │
│  │ ┌────────────────────────┐   │    │
│  │ │ ✗ 你的答案：B           │   │    │ ← Wrong answer (red)
│  │ └────────────────────────┘   │    │
│  │ ┌────────────────────────┐   │    │
│  │ │ ✓ 正确答案：C           │   │    │ ← Correct answer (green)
│  │ └────────────────────────┘   │    │
│  │                              │    │
│  │ 电解质定义：在水溶液或       │    │ ← Explanation
│  │ 熔融状态下能导电的化合物...   │    │
│  │                              │    │
│  │ ┌──────────┐ ┌──────────┐   │    │
│  │ │ 生成变式题 │ │  已掌握   │   │    │ ← Action buttons
│  │ └──────────┘ └──────────┘   │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ #2 [审题障碍型]            ▶  │    │ ← Card 2 header (collapsed)
│  │ 关于化学键类型的判断...       │    │ ← One-line summary
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ #3 [表述障碍型]            ▶  │    │ ← Card 3 header (collapsed)
│  │ 用化学方程式表示...           │    │
│  └──────────────────────────────┘    │
│                                      │
├──────────────────────────────────────┤
│   💬       📝       ❌       👤       │ ← Tab bar (56px)
│  AI助教    练习     错题     我的      │   "错题" active
└──────────────────────────────────────┘
```
