# Google Stitch Prompt: Student Profile & Report (m/report.html)

---

Generate a single, self-contained HTML file (`m/report.html`) for a student mobile profile and weekly report page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Modal overlay**: `rgba(0,0,0,0.4)`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif`; Code — `'JetBrains Mono', monospace` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Modal `16px 16px 0 0`, Badge `12px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
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

---

## Component 1 — Top Title Bar

`height: 56px`, Oxford Blue `#002045` background, `display: flex`, `align-items: center`, `justify-content: center`, `padding: 0 12px`, `position: relative`:

- **Center — Title**: "我的" (My Profile), `16px`, bold, white, IBM Plex Sans
- **Right — Settings gear icon**: Unicode `⚙`, white, `22px`, `cursor: pointer`, `position: absolute`, `right: 12px`, `top: 50%`, `transform: translateY(-50%)`

---

## Component 2 — Personal Info Card

White background card, `border-radius: 8px`, `margin: 16px`, `padding: 20px`, `text-align: center`, `1px solid #e8e5e0`:

- **Avatar**: `80px` diameter circle (`border-radius: 50%`), gray `#e0e0e0` background, `margin: 0 auto`, `display: flex`, `align-items: center`, `justify-content: center`. Inside: the character "张", `28px`, gray `#999`, Cormorant Garamond, bold.
- **Name**: "张三" (Zhang San), `18px`, bold, Oxford Blue `#002045`, Cormorant Garamond, `margin-top: 12px`
- **Class**: "高一(3)班" (Grade 10 Class 3), `14px`, gray `#888`, IBM Plex Sans, `margin-top: 4px`
- **Binding code** (`margin-top: 12px`, `display: inline-flex`, `align-items: center`, `gap: 6px`):
  - Label "绑定码": `12px`, gray `#888`, IBM Plex Sans
  - Code "X7K2M9": `14px`, `'JetBrains Mono', monospace`, gray `#f5f5f5` background, `padding: 4px 8px`, `border-radius: 4px`, letter-spacing `1px`, `user-select: all`, `cursor: text`
  - Subtle copy icon (Unicode `📋` or two overlapping squares) next to the code, `12px`, gray, to suggest it's copyable

---

## Component 3 — Learning Statistics Row

A flexbox row with **3 equal-width columns**, `margin: 16px`, `gap: 0` (a single white card divided by vertical dividers), white background, `border-radius: 8px`, `padding: 16px 8px`, `1px solid #e8e5e0`:

Each column: `flex: 1`, `text-align: center`. Columns separated by `1px solid #f0ede8` vertical dividers (use `border-right` on columns except the last).

Inside each column (top to bottom):

- **Number**: `22px`, bold, Oxford Blue `#002045`, IBM Plex Sans
- **Label**: `12px`, gray `#888`, IBM Plex Sans, `margin-top: 4px`

| Number | Label      |
|--------|------------|
| 85题   | 完成练习   |
| 73%    | 正确率     |
| 12天   | 连续打卡   |

---

## Component 4 — Feature Menu List

A single white card, `border-radius: 8px`, `margin: 0 16px 16px`, `1px solid #e8e5e0`, `overflow: hidden` (to clip border-radius on the first and last items).

**5 menu items.** Each item:

- `height: 48px`, `padding: 0 16px`, `display: flex`, `align-items: center`, `justify-content: space-between`, `cursor: pointer`
- `border-bottom: 1px solid #f0f0f0` (except the last item)
- `transition: background 0.15s`
- Hover: `background: #fafafa`

**Left side — Item label:**
- `font-size: 15px`, `color: #333`, IBM Plex Sans

**Right side — Badge or arrow:**

| # | Label      | Right Content                                             |
|---|------------|-----------------------------------------------------------|
| 1 | 学习报告   | Red "新" badge: red `#e53935` bg, white text `10px`, `border-radius: 10px`, `padding: 2px 8px`, `font-weight: 500` |
| 2 | 学习计划   | Gray `>` arrow, `14px`, `color: #ccc`                     |
| 3 | 我的错题本 | Gray circular badge: gray `#e8e5e0` bg, text "23", `12px`, `min-width: 22px`, `height: 22px`, `border-radius: 50%`, `text-align: center`, `line-height: 22px`, `color: #666`, `font-size: 12px` |
| 4 | 复习中心   | Gray circular badge: same style, text "8"                  |
| 5 | 个人设置   | Gray `>` arrow, `14px`, `color: #ccc`                     |

The "学习报告" item (item 1) is special: clicking it opens the weekly report modal. All other items are static (no action needed for the prototype).

---

## Component 5 — Weekly Report Modal (Bottom Sheet)

### Structure

The modal consists of two elements, both `position: fixed` within the container (or use `position: absolute` relative to `.container`):

#### Overlay
- `position: fixed`, `inset: 0` (covers the full viewport within the 390px container)
- `background: rgba(0,0,0,0.4)`, `z-index: 200`
- Default state: `opacity: 0`, `pointer-events: none`, `transition: opacity 0.3s ease`
- Active state (`.open`): `opacity: 1`, `pointer-events: auto`
- Clicking the overlay closes the modal

#### Bottom Sheet Panel
- `position: fixed`, `bottom: 0`, `left: 50%`, `transform: translateX(-50%)`, `width: 390px` (match container)
- `max-height: 70vh`, `background: white`, `border-radius: 16px 16px 0 0`
- `overflow-y: auto`, `z-index: 201`
- `box-shadow: 0 -4px 20px rgba(0,0,0,0.15)`
- Default state: `transform: translateX(-50%) translateY(100%)`, `transition: transform 0.3s ease`
- Active state (`.open`): `transform: translateX(-50%) translateY(0)`

#### Drag Handle (visual hint)
- A small `36px` wide, `4px` tall, `border-radius: 2px`, gray `#d5d0c8` handle, centered at the top of the panel (`margin: 8px auto 0`)

### Sheet Content (`padding: 20px`)

#### Title Row
`display: flex`, `justify-content: space-between`, `align-items: center`, `margin-bottom: 20px`:
- **Title**: "学习周报（7月第1周）" (Weekly Report — July Week 1), `18px`, bold, Oxford Blue `#002045`, Cormorant Garamond
- **Close button**: `✕` (Unicode), `18px`, gray `#999`, `cursor: pointer`, `padding: 4px`

#### Weekly Stats Overview
A flexbox row of **3 equal columns**, `gap: 8px`, `margin-bottom: 20px`. Each column: white background, `border-radius: 8px`, `padding: 12px 8px`, `text-align: center`, `1px solid #e8e5e0`, `flex: 1`:

| Number | Label      |
|--------|------------|
| 15题   | 本周练习   |
| 80%    | 正确率     |
| 2.5h   | 学习时长   |

Numbers: `20px`, bold, Oxford Blue `#002045`. Labels: `11px`, gray `#888`, `margin-top: 4px`.

#### Knowledge Point Mastery Section

Section subtitle: "知识点掌握度" (Knowledge Point Mastery), `14px`, bold, Oxford Blue, `margin-bottom: 12px`.

**5 knowledge point rows**, `margin-bottom: 12px` each (last one no margin). Each row:

- **Label row** (`display: flex`, `justify-content: space-between`, `margin-bottom: 4px`):
  - Knowledge point name: `13px`, `color: #555`, IBM Plex Sans
  - Percentage: `13px`, bold, Oxford Blue `#002045`

- **Progress bar track**: `width: 100%`, `height: 6px`, `border-radius: 3px`, `background: #e8e5e0`
- **Progress bar fill**: Oxford Blue `#002045`, `height: 100%`, `border-radius: 3px`, width set via inline `style` as percentage

| Knowledge Point    | Mastery |
|--------------------|---------|
| 氧化还原反应       | 85%     |
| 离子反应           | 72%     |
| 化学键与分子结构   | 90%     |
| 元素周期律         | 68%     |
| 化学平衡           | 55%     |

The last one (化学平衡 at 55%) could use an amber or orange color (`#e6a817`) instead of Oxford Blue to indicate it needs attention — a nice detail.

#### Teacher Comment

`margin-top: 20px`, `padding: 14px`, `background: #faf8f5`, `border-radius: 8px`, `border-left: 3px solid #13696a` (Teal accent):

- Small label "教师评语" (Teacher Comment): `11px`, gray `#888`, text-transform uppercase, letter-spacing, `margin-bottom: 6px`
- Comment text: "张同学本周表现不错，氧化还原反应部分掌握较好，离子反应的正确率有明显提升。建议加强对化学平衡章节的练习，特别是勒夏特列原理的应用部分。继续保持！💪" — `14px`, `color: #555`, `line-height: 1.6`, IBM Plex Sans

#### Close Button
- Full width, `height: 44px`, `margin-top: 20px`, `margin-bottom: 8px`
- Gray `#e8e5e0` background, text `#666`
- `border-radius: 8px`, `border: none`, `font-size: 14px`, `font-weight: 500`, `cursor: pointer`
- Text: "关闭" (Close)
- Hover: `background: #d5d0c8`
- Clicking closes the modal

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### Modal Open/Close:
1. Click the "学习报告" menu item → add `.open` class to both the overlay and the bottom sheet panel.
   - Overlay: `opacity: 1`, `pointer-events: auto`
   - Panel: `transform: translateX(-50%) translateY(0)`
2. Close modal (three ways):
   - Click the ✕ close button in the title row
   - Click the "关闭" button at the bottom of the sheet
   - Click the dark overlay
   - All three trigger: remove `.open` class → overlay `opacity: 0, pointer-events: none`, panel `transform: translateX(-50%) translateY(100%)`
3. Use CSS `transition` for smooth animation (0.3s ease).
4. When the modal is open, prevent body scroll on the main page behind it (optional, nice-to-have: set `overflow: hidden` on the container).

### Bottom Tab Bar:
- "我的" tab is active (Oxford Blue `#002045` icon + text).
- Other tabs inactive (gray `#999`).
- Clicking other tabs updates visual state only.

### Copy Binding Code (nice-to-have):
- Clicking the binding code or the copy icon shows a brief "已复制" (Copied) tooltip or changes the icon briefly to ✓ for 1 second, then restores.

---

## Common — Bottom 4-Tab Navigation Bar

`position: fixed` (within container), `bottom: 0`, `width: 100%` (max 390px), `height: 56px`, `background: white`, `border-top: 1px solid #eee`, `display: flex`, `justify-content: space-around`, `align-items: center`, `z-index: 50`, `padding-bottom: env(safe-area-inset-bottom, 0)`.

4 tabs (flex: 1, centered column, cursor pointer):

| Tab   | Icon | Label | State    |
|-------|------|-------|----------|
| AI助教 | 💬  | AI助教 | Inactive (gray #999) |
| 练习   | 📝  | 练习   | Inactive (gray #999) |
| 错题   | ❌  | 错题   | Inactive (gray #999) |
| 我的   | 👤  | 我的   | **Active** (Oxford Blue #002045) |

Each tab: icon `20px`, label `10px` with `4px` margin-top.

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond (400, 700), IBM Plex Sans (400, 500), and JetBrains Mono (400) via a `<link>` in `<head>`.
- **Global box-sizing**: `border-box`.
- **Body styling**: `margin: 0`, `padding: 0`, `background: #e8e5e0`.
- **Container**: `max-width: 390px`, `margin: 0 auto`, `min-height: 100vh`, `background: #faf8f5`, `position: relative`, `display: flex`, `flex-direction: column`, `box-shadow: 0 0 20px rgba(0,0,0,0.05)`. `overflow-x: hidden` is important — it keeps the modal contained.
- **Icons**: Unicode characters only (⚙ gear, ✕ close, 💬📝❌👤 tabs, 📋 copy, ✓ check, > arrow). No icon libraries.
- **No images**: all visuals are CSS circles, text, colored divs.
- **Modal bottom sheet**: the slide-up pattern should feel native and smooth. The `translateY` transition is key — start at `100%` (below screen), end at `0` (visible). The border-radius `16px 16px 0 0` on the top corners gives the characteristic bottom-sheet look.
- **Menu list**: clean iOS-style list with dividers, right-aligned badges/arrows. The red "新" badge on "学习报告" draws attention to the modal trigger.
- **Content area**: `flex: 1`, `overflow-y: auto`, `padding-bottom: 70px` to clear the tab bar.
- **Binding code**: monospace font + gray background makes it look like a copyable code snippet. The `user-select: all` CSS makes it easy to select on click.
- **Smooth transitions**: modal slide 0.3s ease, button hovers, menu item hover.
- **Mobile feel**: the page should feel like a personal profile hub — clean, organized, with the weekly report as a delightful surprise (the red "新" badge creates anticipation). The modal should feel native and satisfying to open/close.

---

## Visual Structure Summary

```
┌──────────────────────────────────────┐
│              我的              ⚙     │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────┤
│  ┌──────────────────────────────┐    │
│  │          ┌──────┐            │    │
│  │          │  张  │            │    │ ← Avatar (80px circle)
│  │          └──────┘            │    │
│  │           张三               │    │ ← Name
│  │         高一(3)班            │    │ ← Class
│  │    绑定码  [X7K2M9] 📋       │    │ ← Binding code
│  └──────────────────────────────┘    │
│                                      │
│  ┌─────────┬─────────┬─────────┐    │
│  │  85题   │   73%   │  12天   │    │ ← Stats row
│  │ 完成练习 │  正确率  │ 连续打卡 │    │
│  └─────────┴─────────┴─────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 学习报告              [新]   │    │ ← Menu list
│  │ ─────────────────────────── │    │
│  │ 学习计划                >   │    │
│  │ ─────────────────────────── │    │
│  │ 我的错题本             (23) │    │
│  │ ─────────────────────────── │    │
│  │ 复习中心                (8) │    │
│  │ ─────────────────────────── │    │
│  │ 个人设置                >   │    │
│  └──────────────────────────────┘    │
│                                      │
├──────────────────────────────────────┤
│   💬       📝       ❌       👤       │ ← Tab bar (56px)
│  AI助教    练习     错题     我的      │   "我的" active
└──────────────────────────────────────┘

        ┌──────────────────────────────┐
        │  ━━━━━━━━  (drag handle)     │
        │                              │
        │  学习周报（7月第1周）    ✕    │ ← Modal title
        │                              │
        │  ┌──────┬──────┬──────┐      │
        │  │ 15题 │  80% │ 2.5h │      │ ← Weekly stats
        │  │本周练习│ 正确率│学习时长│      │
        │  └──────┴──────┴──────┘      │
        │                              │
        │  知识点掌握度                  │
        │  氧化还原反应     ████░ 85%   │ ← Progress bars
        │  离子反应         ███░░ 72%   │
        │  化学键与分子结构 ████░ 90%   │
        │  元素周期律       ███░░ 68%   │
        │  化学平衡         ██░░░ 55%   │ ← Amber (needs work)
        │                              │
        │  ┌────────────────────────┐  │
        │  │ 教师评语               │  │ ← Teacher comment
        │  │ 张同学本周表现不错...    │  │
        │  └────────────────────────┘  │
        │                              │
        │  ┌────────────────────────┐  │
        │  │          关闭           │  │ ← Close button
        │  └────────────────────────┘  │
        └──────────────────────────────┘
        Bottom sheet (slides up from bottom, max-height 70vh)
```
