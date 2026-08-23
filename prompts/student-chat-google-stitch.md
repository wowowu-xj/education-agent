# Google Stitch Prompt: Student AI Tutor Chat (m/index.html)

---

Generate a single, self-contained HTML file (`m/index.html`) for a student mobile AI tutor chat page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **AI message bubble**: background `#e0f2f1`, text `#1a3a3a`
- **User message bubble**: white background, `1px solid #ddd`
- **Background**: warm paper `#faf8f5`
- **Sidebar background**: dark `#1a1a2e`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Message bubbles `12px`, Buttons `8px`, Chips `16px`, Input `20px`
- **Target viewport**: Mobile — `max-width: 390px`, centered with `margin: 0 auto`
- **Body background**: `#e8e5e0` (so the phone container stands out on desktop)

---

## Page Structure

The entire page is wrapped in a container:

```css
.container {
  max-width: 390px;
  min-height: 100vh;
  margin: 0 auto;
  background: #faf8f5;
  position: relative;
  overflow-x: hidden;
}
```

The container uses `position: relative` and `overflow-x: hidden` to clip the sidebar when it slides out.

---

## Component 1 — Top Title Bar

Fixed at the top of the container (`position: relative` within `.container`), `height: 56px`, Oxford Blue `#002045` background, `display: flex`, `align-items: center`, `padding: 0 12px`, `z-index: 50`:

**Left — Hamburger menu icon:**
- Three horizontal white lines, each `18px` wide, `2px` tall, `2px` gap between them, white `#fff`
- Built with three `<span>` or `<div>` elements stacked vertically inside a `24px` square clickable area
- `cursor: pointer`
- Clicking toggles the sidebar drawer open/closed

**Center — App title:**
- "ChemAI 助教" (ChemAI Tutor), `16px`, `bold`, white, IBM Plex Sans
- Absolutely centered in the bar (use `position: absolute; left: 50%; transform: translateX(-50%)` on the title, with the bar as `position: relative`)

**Right — New chat icon:**
- A "+" icon or square edit icon (use Unicode `✎` or `+` inside a `24px` square), white
- `cursor: pointer`
- `margin-left: auto` (pushes to the right)

---

## Component 2 — Sidebar Drawer

A slide-out drawer from the left edge:

**Drawer panel:**
- `position: fixed` (relative to the `.container` or use absolute), `top: 0`, `left: -280px`, `width: 280px`, `height: 100%`, `background: #1a1a2e`, `z-index: 100`, `transition: left 0.3s ease`
- When open: `left: 0` (applied via JavaScript adding a `.open` class)
- `display: flex`, `flex-direction: column`, `overflow-y: auto`

**Overlay:**
- `position: fixed`, `inset: 0` (covers the entire container), `background: rgba(0,0,0,0.4)`, `z-index: 99`
- Default: `opacity: 0`, `pointer-events: none`, `transition: opacity 0.3s`
- When open: `opacity: 1`, `pointer-events: auto`
- Clicking the overlay closes the drawer

**Sidebar content (top to bottom):**

### Student Info Section
- `padding: 20px`
- Avatar placeholder: `48px` diameter circle, gray `#555` background, white initials "张" centered, `font-size: 18px`, `margin-bottom: 12px`
- Name: "张三" (Zhang San), white `#fff`, `16px`, bold, IBM Plex Sans
- Class: "高一(3)班" (Grade 10 Class 3), gray `#999`, `13px`, `margin-top: 4px`

### Divider
- `height: 1px`, `background: rgba(255,255,255,0.1)`, `margin: 0 20px`

### Conversation History List
- Section label: "历史对话" (History), gray `#888`, `12px`, text-transform uppercase, `padding: 16px 20px 8px`
- 5 history items, each: `padding: 12px 20px`, `cursor: pointer`, `transition: background 0.15s`
  - Hover: `background: rgba(255,255,255,0.05)`
  - Title: white `#fff`, `14px`
  - Timestamp: gray `#777`, `12px`, `margin-top: 4px`

  Data:
  1. "氧化还原反应答疑" — 今天 14:30
  2. "化学方程式配平练习" — 今天 10:15
  3. "离子反应知识点总结" — 昨天 16:42
  4. "期中考试错题分析" — 昨天 09:20
  5. "元素周期律复习" — 7月15日

### Spacer
- `flex: 1` (pushes the logout button to the bottom)

### Logout Button
- `padding: 20px`
- Text: "退出登录" (Logout), `14px`, color `#c0392b` (red), `cursor: pointer`
- Subtle hover: text color brightens to `#e74c3c`

---

## Component 3 — Chat Message Area

A scrollable area between the top bar and the input area:

- `flex: 1`, `overflow-y: auto`, `background: #faf8f5`, `padding: 16px`
- **Bottom padding**: at least `126px` to account for the quick chips row, input area, and bottom tab bar
- `display: flex`, `flex-direction: column`, `gap: 12px`

### AI Message Bubbles (3 messages — left-aligned)

Each AI bubble:
- Background `#e0f2f1`
- `border-radius: 12px`, with bottom-left corner at `4px` (gives a "speech bubble tail" feel — use `border-bottom-left-radius: 4px`)
- `padding: 12px 14px`
- `max-width: 80%`
- `align-self: flex-start` (left-aligned)
- `font-size: 14px`, IBM Plex Sans, `color: #1a3a3a`, `line-height: 1.6`
- `word-wrap: break-word`

Content for the 3 AI messages:

1. "你好张三！我是 ChemAI 助教，可以帮你解答化学学习中的问题。你可以直接提问，也可以点击下方的快捷入口开始学习。😊"

2. "氧化还原反应的实质是**电子的转移**（或电子对的偏移）。记住一个口诀：**升失氧，降得还** — 化合价升高、失去电子、被氧化；化合价降低、得到电子、被还原。"

3. "离子反应发生的条件是：生成**沉淀**、**气体**、**弱电解质**或发生**氧化还原反应**。需要我针对某个条件展开讲解吗？"

### User Message Bubbles (2 messages — right-aligned)

Each user bubble:
- White background `#fff`
- `border: 1px solid #ddd`
- `border-radius: 12px`, with bottom-right corner at `4px` (`border-bottom-right-radius: 4px`)
- `padding: 12px 14px`
- `max-width: 80%`
- `align-self: flex-end` (right-aligned)
- `font-size: 14px`, IBM Plex Sans, `color: #333`, `line-height: 1.6`

Content for the 2 user messages:

1. "什么是氧化还原反应？帮我解释一下"

2. "那离子反应发生的条件是什么？"

### Timestamps (optional subtle detail)
- Below each bubble, a tiny `11px` gray `#bbb` timestamp, `margin-top: 2px`
- AI timestamps left-aligned, user timestamps right-aligned
- Times: 14:28, 14:29, 14:30, 14:31, 14:32 (spread across the 5 messages)

---

## Component 4 — Quick Suggestion Chips Row

A horizontally scrollable row of suggestion chips, positioned between the chat area and the input:

- `overflow-x: auto`, `white-space: nowrap`
- `padding: 12px 16px`
- `background: white`
- `border-top: 1px solid #eee`
- Hide scrollbar visually but keep it functional: `::-webkit-scrollbar { display: none; }` or `scrollbar-width: none`
- `display: flex`, `gap: 8px`

**5 chips** (pill-shaped buttons):
- White background, `1px solid #ddd`, `border-radius: 16px`, `padding: 8px 16px`, `font-size: 13px`, IBM Plex Sans, `color: #555`
- `cursor: pointer`, `flex-shrink: 0` (prevent shrinking)
- Hover: border color changes to Oxford Blue `#002045`, text color changes to `#002045`
- Transition: `border-color 0.15s, color 0.15s`

Chip labels:
1. "帮我讲解这个知识点"
2. "配平这个方程式"
3. "做几道练习题"
4. "查看我的错题"
5. "总结今天学习"

---

## Component 5 — Bottom Input Area

A sticky input bar, `position: sticky`, `bottom: 56px` (above the tab bar), `z-index: 10`:

- `height: 70px`
- `background: white`
- `border-top: 1px solid #eee`
- `padding: 8px 12px`
- `display: flex`, `align-items: center`, `gap: 8px`

**Left — Attachment icon:**
- Unicode 📎 (paperclip) or a "+" in a circle
- `24px` square, gray `#999`, `cursor: pointer`
- `flex-shrink: 0`

**Center — Text input:**
- `flex: 1`, `height: 40px`, `border-radius: 20px` (pill-shaped)
- `background: #f0f0f0`, `border: none`, `padding: 0 16px`
- `font-size: 14px`, IBM Plex Sans
- Placeholder: "输入你的问题..." (Type your question...)
- `outline: none`
- Focus state: background slightly darkens to `#e8e8e8`

**Right — Send button:**
- `40px × 40px` circle (`border-radius: 50%`)
- Oxford Blue `#002045` background
- White upward-pointing arrow inside (use Unicode `↑` or `➤` at `16px`, white, centered)
- `cursor: pointer`, `flex-shrink: 0`
- Hover: background slightly lighter `#003060`
- Transition: `background 0.15s`

---

## Component 6 — Bottom 4-Tab Navigation Bar

A fixed-bottom tab bar:

- `position: fixed` (within container: `position: absolute`), `bottom: 0`, `left: 0`, `right: 0` (or `width: 100%`)
- `height: 56px`
- `background: white`
- `border-top: 1px solid #eee`
- `display: flex`, `justify-content: space-around`, `align-items: center`
- `z-index: 50`
- `padding-bottom: env(safe-area-inset-bottom, 0)` for notched phones

**4 tabs, equal width (flex: 1 each). Each tab is a flexbox column, centered:**

| Tab     | Icon (CSS/Unicode)                          | Label       | State    |
|---------|---------------------------------------------|-------------|----------|
| AI助教  | 💬 or a CSS speech-bubble shape (20×20px)   | AI助教      | Active   |
| 练习    | 📝 or a CSS pencil shape (20×20px)          | 练习        | Inactive |
| 错题    | ❌ or a CSS X-mark (20×20px)                | 错题        | Inactive |
| 我的    | 👤 or a CSS person circle (20×20px)         | 我的        | Inactive |

**Active tab styling (AI助教):**
- Icon color: Oxford Blue `#002045`
- Label color: Oxford Blue `#002045`
- Label: `10px`, IBM Plex Sans, `margin-top: 4px`

**Inactive tab styling:**
- Icon color: gray `#999`
- Label color: gray `#999`
- Same sizing

Each tab: `cursor: pointer`, `transition: color 0.15s`.

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### Sidebar Drawer:
1. Click the hamburger menu icon → add `.open` class to the sidebar (`left: 0`) and show overlay (`opacity: 1`, `pointer-events: auto`)
2. Click the overlay → remove `.open` class from sidebar (`left: -280px`) and hide overlay (`opacity: 0`, `pointer-events: none`)
3. Click a history conversation item → close the drawer (same as overlay click)
4. Use CSS `transition: left 0.3s ease` and `transition: opacity 0.3s` for smooth animation

### Chat Input (cosmetic only — static prototype):
- Clicking the send button briefly adds the input text as a new user bubble at the bottom of the chat area (nice-to-have, but not required — the page can be fully static except for the sidebar toggle)
- If implementing: clone a user bubble template, set its text, append to chat area, scroll to bottom, clear input

### Chip Click (cosmetic only):
- Clicking a suggestion chip populates the input field with that text (nice-to-have)

### Tab Switching:
- Clicking a bottom tab updates the active state (icon + label color) for visual feedback
- No actual page navigation needed — this is a single-page prototype

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond (400, 700) and IBM Plex Sans (400, 500) via a `<link>` in `<head>`.
- **Global box-sizing**: `border-box`.
- **Body styling**: `margin: 0`, `padding: 0`, `background: #e8e5e0` (desktop backdrop).
- **Container**: `max-width: 390px`, `margin: 0 auto`, `position: relative`, `overflow-x: hidden`, `min-height: 100vh`, `background: #faf8f5`.
- **Icons**: use Unicode characters (☰ or ≡ for hamburger, ✎ or + for new chat, 📎 for attachment, ↑ for send, 💬 📝 ❌ 👤 for tab icons) or simple CSS shapes. No icon libraries.
- **No images**: avatars are CSS circles with text, icons are Unicode/CSS.
- **Chat scroll**: the chat area should be independently scrollable. Use `flex: 1` and `overflow-y: auto`.
- **Message bubble tails**: use `border-bottom-left-radius: 4px` on AI bubbles and `border-bottom-right-radius: 4px` on user bubbles for a subtle speech-bubble effect.
- **Smooth transitions**: sidebar slide (0.3s ease), overlay fade (0.3s), button hovers, tab state changes.
- **Mobile feel**: the page should feel like a native chat app — clean, minimal, with natural message flow. The AI bubbles should feel warm and helpful (teal-tinted), while user bubbles are clean white cards.

---

## Visual Structure Summary

```
┌──────────────────────────────────────────┐
│  ≡           ChemAI 助教          ✎      │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────┐            │
│  │ 你好张三！我是 ChemAI     │            │ ← AI bubble (#e0f2f1)
│  │ 助教，可以帮你解答...     │            │
│  └──────────────────────────┘            │
│                      14:28               │
│                                          │
│        ┌────────────────────┐            │
│        │ 什么是氧化还原反应？ │            │ ← User bubble (white)
│        └────────────────────┘            │
│                             14:29        │
│                                          │
│  ┌──────────────────────────┐            │
│  │ 氧化还原反应的实质是      │            │ ← AI bubble
│  │ 电子的转移...             │            │
│  │ 升失氧，降得还            │            │
│  └──────────────────────────┘            │
│                      14:30               │
│                                          │
│        ┌─────────────────────┐           │
│        │ 那离子反应发生的     │           │ ← User bubble
│        │ 条件是什么？         │           │
│        └─────────────────────┘           │
│                             14:31        │
│                                          │
│  ┌──────────────────────────┐            │
│  │ 离子反应发生的条件是...    │            │ ← AI bubble
│  └──────────────────────────┘            │
│                      14:32               │
│                                          │
│  (scrollable area, padding-bottom: 126px)│
├──────────────────────────────────────────┤
│ ← scroll →                               │
│ [帮我讲解] [配平方程式] [做练习题] [错题] [总结] │ ← Quick chips
├──────────────────────────────────────────┤
│  📎  ┌────────────────────┐  (●)         │ ← Input bar (70px, sticky)
│      │ 输入你的问题...      │  ↑           │
│      └────────────────────┘              │
├──────────────────────────────────────────┤
│   💬       📝       ❌       👤           │ ← Tab bar (56px, fixed bottom)
│  AI助教    练习     错题     我的          │
└──────────────────────────────────────────┘

    ┌──────────────┐
    │  张三         │ ← Sidebar drawer
    │  高一(3)班    │   (280px, dark #1a1a2e)
    │ ──────────── │   slides in from left
    │  历史对话      │
    │  氧化还原...   │
    │  方程式配平... │
    │  离子反应...   │
    │  期中考试...   │
    │  元素周期律... │
    │              │
    │  退出登录      │
    └──────────────┘
```
