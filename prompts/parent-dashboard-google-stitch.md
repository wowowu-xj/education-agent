# Google Stitch Prompt: Parent Main Dashboard (m/parent.html)

---

Generate a single, self-contained HTML file (`m/parent.html`) for a parent mobile dashboard page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

The page has **3 tabs** controlled by JavaScript. Only one tab panel is visible at a time. Additionally, a **floating AI button** triggers a bottom-sheet panel.

**Priority**: Ensure the page framework (top bar, child selector, tab bar) and **Tab 1 (概览)** are fully detailed. Tabs 2 and 3 can be simpler but functional.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Obstacle segment colors**:
  - 概念理解 (Concept): Purple `#7B2D8E`
  - 审题障碍 (Exam Reading): Blue `#3B5BA5`
  - 表述障碍 (Expression): Cyan `#00897B`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Chips `16px`, Modal panel `16px 16px 0 0`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `16px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Floating AI button**: `56px × 56px` circle, Oxford Blue `#002045` bg, `box-shadow: 0 4px 12px rgba(0,32,69,0.3)`
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
  overflow-x: hidden;
}
```

**No bottom tab bar** — the parent app is a single-page dashboard.

---

## Component 1 — Top Title Bar

`height: 56px`, Oxford Blue `#002045` background, `display: flex`, `align-items: center`, `justify-content: space-between`, `padding: 0 12px`:

- **Left**: "家长中心" (Parent Center), `16px`, bold, white, IBM Plex Sans
- **Right** (`display: flex`, `gap: 16px`, `align-items: center`):
  - Settings gear: Unicode `⚙`, white, `20px`, `cursor: pointer`
  - Logout/exit: Unicode `↩` or a door-arrow icon, white, `20px`, `cursor: pointer`

---

## Component 2 — Child Selector

White background, `padding: 12px 16px`, `text-align: center`, `border-bottom: 1px solid #eee`:

- **Horizontal selector row** (`display: flex`, `align-items: center`, `justify-content: center`):
  - Left arrow: `<` (Unicode `‹` or `<`), `18px`, gray `#999`, `cursor: pointer`, `padding: 4px`
  - Child name: "张三" (Zhang San), `16px`, bold, Oxford Blue `#002045`, IBM Plex Sans, `margin: 0 16px`
  - Right arrow: `>` (Unicode `›` or `>`), `18px`, gray `#999`, `cursor: pointer`, `padding: 4px`
  - Clicking arrows could cycle through children — for the prototype, just visual arrows.

- **Bottom link**: "绑定新子女" (Bind New Child), Teal `#13696a`, `13px`, `display: block`, `margin-top: 4px`, `cursor: pointer`, `text-decoration: none`. Add a small `+` icon before the text.

---

## Component 3 — Tab Bar

`height: 44px`, `display: flex`, `border-bottom: 1px solid #eee`, `background: white`:

Three equal-width tabs (`flex: 1`, `text-align: center`, `line-height: 44px`, `font-size: 14px`, IBM Plex Sans, `cursor: pointer`, `position: relative`):

1. **"概览" (Overview)** — **Active by default**: Oxford Blue `#002045` text, `font-weight: 500`. A `2px` Oxford Blue underline at the bottom (`position: absolute`, `bottom: 0`, `left: 50%`, `transform: translateX(-50%)`, `width: 40px`).
2. **"学习报告" (Learning Report)** — Inactive: gray `#999` text, no underline.
3. **"消息" (Messages)** — Inactive: gray `#999` text, no underline.

**JS behavior**: Clicking a tab updates the active state (text color + underline) and shows the corresponding panel (`display: block`), hiding the other two (`display: none`).

---

## Tab 1 — 概览 (Overview) — Default Visible

`padding: 16px`, `overflow-y: auto`, `display: flex`, `flex-direction: column`, `gap: 12px`.

### 4. 2×2 Statistics Card Grid

CSS Grid: `grid-template-columns: repeat(2, 1fr)`, `gap: 12px`.

Each stat card: white background, `border-radius: 8px`, `padding: 16px`, `1px solid #e8e5e0`.

| Card | Top Label (12px gray) | Value / Content                          |
|------|-----------------------|------------------------------------------|
| 1    | 本周练习              | **12题** (22px, Oxford Blue, bold)       |
| 2    | 正确率                | **75%** (22px, Oxford Blue, bold)        |
| 3    | 薄弱知识点            | "化学方程式配平" (Purple `#7B2D8E` chip, 12px, `border-radius: 16px`, `padding: 3px 10px`, white text, `margin-top: 4px`) |
| 4    | 最近学习              | "7月10日 19:30" (14px, bold, Oxford Blue, `margin-top: 4px`) |

For cards 3 and 4, the value sits below the label with a small gap.

### 5. "学习特点分析" Card (Learning Characteristic Analysis)

White card, `border-radius: 8px`, `padding: 16px`, `1px solid #e8e5e0`:

- **Title**: "学习特点分析" (Learning Characteristic Analysis), `16px`, bold, Oxford Blue `#002045`, Cormorant Garamond, `margin-bottom: 12px`

- **Obstacle distribution bar**: a horizontal segmented bar, `height: 6px`, `border-radius: 3px`, full width. Three colored segments laid out horizontally (use flexbox with percentage widths):
  - 概念理解 30%: Purple `#7B2D8E`
  - 审题障碍 50%: Blue `#3B5BA5`
  - 表述障碍 20%: Cyan `#00897B`
  Total = 100%.

- **Legend row** below the bar (`margin-top: 8px`, `display: flex`, `gap: 12px`, `font-size: 11px`):
  - ● 概念理解 30% (purple dot + name + %)
  - ● 审题障碍 50% (blue dot)
  - ● 表述障碍 20% (cyan dot)

- **Analysis text** (`margin-top: 10px`, `font-size: 14px`, `color: #666`, `line-height: 1.6`):
  "孩子审题能力有待加强，建议多读题目要求，圈画关键词。概念理解方面表现较好，可以适当增加难度。表述方面基本达标，继续保持。"

### 6. "本周学习建议" Card (Weekly Study Suggestions)

White card, `border-radius: 8px`, `padding: 16px`, `1px solid #e8e5e0`:

- **Title**: "本周学习建议" (Weekly Study Suggestions), `16px`, bold, Oxford Blue `#002045`, Cormorant Garamond, `margin-bottom: 10px`

- **Knowledge point list** — 3 items, each: `display: flex`, `align-items: flex-start`, `gap: 8px`, `margin-bottom: 8px`, `font-size: 14px`, `color: #333`:
  - ● (Oxford Blue bullet, `6px` circle) + "氧化还原反应 — 化合价升降法练习"
  - ● + "离子方程式配平 — 沉淀与气体判断"
  - ● + "化学平衡 — 勒夏特列原理应用题"

- **Family suggestion box** (`margin-top: 12px`, `background: #f9f9f9`, `padding: 12px`, `border-radius: 4px`, `border-left: 3px solid #13696a`):
  - Small label "🏠 家庭建议" (Family Tip), `11px`, gray `#888`, uppercase, `margin-bottom: 4px`
  - Text: "家长可以陪孩子一起梳理化学方程式的配平规则，使用化合价升降法练习。每天花10-15分钟效果最佳。" — `13px`, `color: #555`, `line-height: 1.5`

---

## Tab 2 — 学习报告 (Learning Report) — Simplified

`padding: 16px`, `display: none` by default.

### 7. "学习概览" Card (Learning Overview)

White card, `border-radius: 8px`, `padding: 16px`:

- **Time selector row** (`display: flex`, `align-items: center`, `justify-content: center`, `gap: 16px`, `margin-bottom: 14px`):
  - Left arrow `<`, `14px`, gray `#999`, `cursor: pointer`
  - "7月第1周" (July Week 1), `14px`, bold, Oxford Blue
  - Right arrow `>`, `14px`, gray `#999`, `cursor: pointer`

- **3-column stats** (`display: flex`, `gap: 8px`):
  - 完成练习: **15题** (20px Oxford Blue bold) + label 11px gray
  - 正确率: **80%** + label
  - 学习时长: **2.5h** + label
  Each column: `flex: 1`, `text-align: center`, with `1px solid #f0ede8` dividers.

### 8. "知识点掌握" Card (Knowledge Mastery)

White card, `border-radius: 8px`, `padding: 16px`, `margin-top: 12px`:

- Title: "知识点掌握" (Knowledge Mastery), `14px`, bold, Oxford Blue, `margin-bottom: 12px`

- **5 knowledge point rows**. Each row (`margin-bottom: 10px`):
  - Label + percentage (`display: flex`, `justify-content: space-between`, `font-size: 13px`, `margin-bottom: 4px`)
  - Progress bar: `height: 6px`, `border-radius: 3px`, track `#e8e5e0`, fill Oxford Blue `#002045` (width via inline style)

  | Knowledge Point    | %   |
  |--------------------|-----|
  | 氧化还原反应       | 85% |
  | 离子反应           | 72% |
  | 化学键与分子结构   | 90% |
  | 元素周期律         | 68% |
  | 化学平衡           | 55% |

### 9. "学习特点+家庭建议" Card + AI Interpretation Toggle

White card, `border-radius: 8px`, `padding: 16px`, `margin-top: 12px`:

- Reuse the same obstacle distribution bar and analysis text from Tab 1's Card 5.
- Reuse the same family suggestion box from Tab 1's Card 6.
- **"AI解读" (AI Interpretation) button**: Teal `#13696a` background, white text, full width, `height: 40px`, `border-radius: 8px`, `font-size: 13px`, `margin-top: 8px`, `cursor: pointer`.
- **Expandable AI text** (initially hidden, `max-height: 0`, `overflow: hidden`, `transition: max-height 0.3s ease`):
  - When expanded: `max-height: 300px`, `margin-top: 10px`, `padding: 12px`, `background: #f0faf9`, `border-radius: 6px`, `font-size: 13px`, `color: #444`, `line-height: 1.6`.
  - Content: "根据AI分析，张三同学在化学学习中有以下特点：(1) 概念理解能力较强，能够准确记忆化学术语和定义；(2) 审题时需要更多耐心，建议在做题前先通读题目两遍；(3) 化学计算能力中等，需要加强方程式的配平练习。建议每周安排2-3次专项练习，每次聚焦一个薄弱点。"
  - Click "AI解读" button again to collapse.

---

## Tab 3 — 消息 (Messages) — Simplified

`padding: 0`, `display: none` by default.

### 10. Notification List

A vertical list of message cards. Each card: `padding: 16px`, `border-bottom: 1px solid #f0f0f0`, `cursor: pointer`, `position: relative`, `transition: background 0.15s`, hover `background: #fafafa`.

#### Message 1 — Unread
- **Unread dot**: `6px` blue `#3B5BA5` circle, `position: absolute`, `left: 8px`, `top: 22px` (vertically centered with the title)
- **Title**: "学习报告已生成" (Learning Report Generated), `16px`, bold, `color: #1a1a1a`
- **Preview**: "张三的7月第一周学习报告已生成，点击查看详情" — `14px`, `color: #888`, `margin-top: 4px`, `line-height: 1.4`, truncated to 2 lines (`display: -webkit-box`, `-webkit-line-clamp: 2`, `-webkit-box-orient: vertical`, `overflow: hidden`)
- **Time**: "7月10日", `12px`, `color: #bbb`, `margin-top: 6px`

#### Message 2 — Read
- No blue dot. Title normal weight (`font-weight: 400`), text slightly lighter. Same structure otherwise.
- **Title**: "系统通知" (System Notice), `16px`, `color: #555`
- **Preview**: "ChemAI 智辅化学已更新至 v0.1.0 版本..." — `14px`, `color: #999`
- **Time**: "7月8日", `12px`, `color: #bbb`

#### Message 3 — Unread
- Blue dot. Bold title.
- **Title**: "考试提醒" (Exam Reminder), `16px`, bold, `color: #1a1a1a`
- **Preview**: "高一(3)班将于7月15日进行化学月考..." — `14px`, `color: #888`
- **Time**: "7月5日", `12px`, `color: #bbb`

#### Expand Message Detail (JS Accordion)
- Clicking a message card toggles an expanded detail section below it (using `max-height` transition).
- When expanded: show full message body text (`padding: 8px 0`, `font-size: 14px`, `color: #555`, `line-height: 1.6`, `border-top: 1px solid #f5f5f5`, `margin-top: 8px`).
- For Message 1, the expanded detail: "张三同学在7月第1周（7月3日-7月9日）共完成15道练习，正确率80%，学习时长2.5小时。主要薄弱点：化学平衡（55%掌握度），建议加强此章节的复习。"
- Click again to collapse.

---

## Component 11 — Floating AI Button & Bottom Sheet Panel

### Floating AI Button
`position: fixed`, `bottom: 24px`, `right: 16px` (within the 390px container), `z-index: 100`:

- `56px × 56px` circle (`border-radius: 50%`)
- Oxford Blue `#002045` background
- White "AI" text, `16px`, bold, IBM Plex Sans, centered
- `box-shadow: 0 4px 12px rgba(0,32,69,0.3)`
- `cursor: pointer`
- Subtle pulse animation (optional nice-to-have: `@keyframes pulse { 0%, 100% { box-shadow: 0 4px 12px rgba(0,32,69,0.3); } 50% { box-shadow: 0 4px 24px rgba(0,32,69,0.5); } }`)

### Overlay
`position: fixed`, `inset: 0`, `background: rgba(0,0,0,0.4)`, `z-index: 98`. Default: `opacity: 0`, `pointer-events: none`. Active: `opacity: 1`, `pointer-events: auto`. `transition: opacity 0.3s`. Click overlay to close the AI panel.

### AI Advisor Bottom Sheet Panel
`position: fixed`, `bottom: 0`, `left: 0`, `right: 0`, `height: 60vh`, `background: white`, `border-radius: 16px 16px 0 0`, `z-index: 99`, `box-shadow: 0 -4px 20px rgba(0,0,0,0.15)`, `display: flex`, `flex-direction: column`.

Default state: `transform: translateY(100%)`, `transition: transform 0.3s ease`.
Active state (`.open`): `transform: translateY(0)`.

**Sheet content:**

- **Drag handle**: `36px` wide, `4px` tall, `border-radius: 2px`, gray `#d5d0c8`, centered, `margin: 8px auto 0`, `flex-shrink: 0`

- **Title row** (`padding: 12px 20px`, `display: flex`, `justify-content: space-between`, `align-items: center`, `flex-shrink: 0`):
  - "AI学习顾问" (AI Learning Advisor), `16px`, bold, Oxford Blue, Cormorant Garamond
  - Close button: ✕, `16px`, gray `#999`, `cursor: pointer`

- **Preset question chips** (`padding: 0 20px 12px`, `display: flex`, `flex-wrap: wrap`, `gap: 8px`, `flex-shrink: 0`):
  - 3 pill-shaped chips: white bg, `1px solid #ddd`, `border-radius: 16px`, `padding: 8px 14px`, `font-size: 13px`, `color: #555`, `cursor: pointer`, `flex-shrink: 0`
  - "孩子最近学习状态怎么样？"
  - "如何帮助孩子提高化学成绩？"
  - "给我一些家庭辅导建议"
  - Hover: border Oxford Blue, text Oxford Blue

- **Chat area**: `flex: 1`, `overflow-y: auto`, `padding: 0 20px`, `background: #faf8f5` (placeholder — show a brief AI greeting message): "您好！我是 ChemAI 学习顾问，可以帮您了解孩子的学习情况。您可以直接提问，或点击上方的快捷问题。" — AI bubble style: `background: #e0f2f1`, `border-radius: 12px 12px 12px 4px`, `padding: 12px`, `font-size: 13px`, `color: #1a3a3a`, `line-height: 1.5`, `max-width: 85%`

- **Input bar** (`padding: 12px 16px`, `border-top: 1px solid #eee`, `display: flex`, `gap: 8px`, `align-items: center`, `flex-shrink: 0`):
  - Input: `flex: 1`, `height: 40px`, `border-radius: 20px`, `bg: #f0f0f0`, `border: none`, `padding: 0 16px`, `font-size: 14px`, placeholder "输入您的问题..."
  - Send button: `40px × 40px` circle, Oxford Blue `#002045` bg, white `↑` arrow, `cursor: pointer`, `flex-shrink: 0`

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### Tab Switching:
1. Click a tab → remove active state from all tabs (gray text, no underline), add active state to clicked tab (Oxford Blue text + underline).
2. Hide all tab panels (`display: none`), show the corresponding panel (`display: block`).
3. Default: Tab 1 (概览) active.

### AI Interpretation Toggle (Tab 2):
1. Click "AI解读" button → if collapsed: expand (`max-height: 300px`), change button text to "收起解读". If expanded: collapse (`max-height: 0`), restore button text to "AI解读".
2. Use `transition: max-height 0.3s ease`.

### Message Card Expand (Tab 3):
1. Click a message card → toggle its detail section (`max-height: 0` ↔ `max-height: 200px`).
2. Independent accordions — clicking one does not affect others.

### Floating AI Button & Bottom Sheet:
1. Click floating AI button → add `.open` class to overlay (`opacity: 1, pointer-events: auto`) and AI panel (`transform: translateY(0)`).
2. Close via: ✕ button, overlay click. Remove `.open` class → overlay fades out, panel slides down.
3. Transition: `0.3s ease` for both opacity and transform.

### Child Selector Arrows (cosmetic):
- Clicking `<` or `>` could cycle the name — for the prototype, just visual elements. No actual state change needed.

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond (400, 700) and IBM Plex Sans (400, 500) via a `<link>` in `<head>`.
- **Global box-sizing**: `border-box`.
- **Body styling**: `margin: 0`, `padding: 0`, `background: #e8e5e0`.
- **Container**: `max-width: 390px`, `margin: 0 auto`, `min-height: 100vh`, `background: #faf8f5`, `position: relative`, `display: flex`, `flex-direction: column`, `box-shadow: 0 0 20px rgba(0,0,0,0.05)`, `overflow-x: hidden`.
- **Icons**: Unicode characters only (⚙ settings, ↩ logout, ‹/› arrows, ✕ close, ● bullets, 🏠 home, ✓ check, ↑ send). No icon libraries.
- **No images**: all visuals are CSS shapes, text, colored divs.
- **No bottom tab bar**: unlike student pages, the parent dashboard has no tab navigation — it's a single-page app with its own internal tab system.
- **Tab panels**: use `display: none/block` for tab switching. Tab 1 scrollable independently within its container.
- **Obstacle bar**: the 3-color segmented bar is a key visual that connects to the teacher's diagnosis page. Use consistent purple/blue/cyan colors.
- **Floating AI button**: the `box-shadow` makes it pop. Position it relative to the 390px container, not the full viewport.
- **AI bottom sheet**: the slide-up panel should feel native. `border-radius: 16px 16px 0 0` + drag handle + `translateY` transition.
- **Message unread dots**: blue circles absolutely positioned on the left edge are a clear, standard mobile pattern for unread indicators.
- **Smooth transitions**: tab switch (instant), accordion max-height (0.3s), modal slide (0.3s), button hovers (0.15s).
- **Parent-focused tone**: warm, reassuring, informative. The page should make parents feel informed and empowered, not overwhelmed.

---

## Visual Structure Summary

```
┌──────────────────────────────────────┐
│  家长中心                  ⚙  ↩     │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────┤
│         <  张三  >                   │ ← Child selector
│        + 绑定新子女                   │
├──────────────────────────────────────┤
│  ───概览──────学习报告──────消息───    │ ← 3 Tabs (44px)
│    ████                              │   "概览" active
├──────────────────────────────────────┤
│  Tab 1 — 概览 (visible)              │
│  ┌────────────┬────────────┐        │
│  │ 本周练习    │  正确率     │        │ ← 2×2 stats grid
│  │   12题     │   75%      │        │
│  ├────────────┼────────────┤        │
│  │ 薄弱知识点  │  最近学习   │        │
│  │ [化学方程式]│ 7/10 19:30 │        │
│  └────────────┴────────────┘        │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 学习特点分析                  │    │
│  │ ██████████████████████       │    │ ← Obstacle bar
│  │ 紫色30% 蓝色50% 青色20%      │    │
│  │ 孩子审题能力有待加强...       │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 本周学习建议                  │    │
│  │ ● 氧化还原反应 — 化合价升降法 │    │
│  │ ● 离子方程式配平              │    │
│  │ ● 化学平衡 — 勒夏特列原理     │    │
│  │ ┌────────────────────────┐   │    │
│  │ │ 🏠 家庭建议             │   │    │
│  │ │ 家长可以陪孩子一起...    │   │    │
│  │ └────────────────────────┘   │    │
│  └──────────────────────────────┘    │
│                                      │
│                              ┌──┐    │
│                              │AI│    │ ← Floating AI button
│                              └──┘    │   (fixed bottom-right)
└──────────────────────────────────────┘

When AI button clicked:
┌──────────────────────────────────────┐
│  (overlay: rgba(0,0,0,0.4))          │
│                                      │
│  ┌──────────────────────────────┐    │
│  │  ━━━━━━  (drag handle)       │    │
│  │  AI学习顾问              ✕   │    │
│  │                              │    │
│  │  [孩子最近学习状态？]         │    │ ← Preset chips
│  │  [如何帮助提高成绩？]         │    │
│  │  [给我一些家庭辅导建议]       │    │
│  │                              │    │
│  │  ┌──────────────────────┐    │    │
│  │  │ 您好！我是 ChemAI    │    │    │ ← AI greeting
│  │  │ 学习顾问...          │    │    │
│  │  └──────────────────────┘    │    │
│  │                              │    │
│  │  ┌──────────────────┐  (●)  │    │ ← Input + send
│  │  │ 输入您的问题...    │   ↑   │    │
│  │  └──────────────────┘       │    │
│  └──────────────────────────────┘    │
│         (60vh bottom sheet)          │
└──────────────────────────────────────┘
```
