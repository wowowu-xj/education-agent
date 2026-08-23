# Google Stitch Prompt: Student Practice Page (m/practice.html)

---

Generate a single, self-contained HTML file (`m/practice.html`) for a student mobile practice/exercise page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

The page has **two view states** controlled by JavaScript: (1) Task List View (default), (2) Quiz Interface View. Only one view is visible at a time.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Correct answer**: green background `#e0f2f1`, border `#2c6e49`
- **Wrong answer**: red background `#ffdad6`, border `#c0392b`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Chips `16px`, Progress bar `3px`, Option buttons `8px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `16px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Progress bar**: gray `#e0e0e0` track (`height: 6px`, `border-radius: 3px`), Oxford Blue `#002045` fill
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

## Common — Bottom 4-Tab Navigation Bar

Both views share the same bottom tab bar:

- `position: fixed` (within container), `bottom: 0`, `width: 100%` (max 390px), `height: 56px`
- `background: white`, `border-top: 1px solid #eee`
- `display: flex`, `justify-content: space-around`, `align-items: center`
- `z-index: 50`
- `padding-bottom: env(safe-area-inset-bottom, 0)`

**4 tabs, equal width (flex: 1), each a centered flexbox column:**

| Tab   | Icon | Label | State    |
|-------|------|-------|----------|
| AI助教 | 💬   | AI助教 | Inactive (gray #999) |
| 练习   | 📝   | 练习   | **Active** (Oxford Blue #002045) |
| 错题   | ❌   | 错题   | Inactive (gray #999) |
| 我的   | 👤   | 我的   | Inactive (gray #999) |

Each tab: icon `20px`, label `10px` with `4px` margin-top, `cursor: pointer`.

---

## View 1 — Task List (Default Visible)

### 1.1 Top Title Bar

`height: 56px`, Oxford Blue `#002045` background, `display: flex`, `align-items: center`, `padding: 0 12px`:

- **Left — Back arrow**: Unicode `←` or `‹`, white, `20px`, `cursor: pointer`
- **Center — Title**: "练习" (Practice), `16px`, bold, white, IBM Plex Sans, `position: absolute`, `left: 50%`, `transform: translateX(-50%)`
- **Right — Progress**: "3/10", `13px`, white, IBM Plex Sans, `margin-left: auto`

### 1.2 Sub-Tab Bar

`height: 44px`, `display: flex`, `border-bottom: 2px solid #eee` (or `#f0ede8`):

Two equal-width tabs (`flex: 1`, `text-align: center`, `line-height: 44px`, `font-size: 14px`, IBM Plex Sans, `cursor: pointer`):

- **"待完成(7)"** (Pending, 7) — **Active**:
  - Oxford Blue `#002045` text color
  - `2px` Oxford Blue bottom border (a short underline, or a full-width border on just this tab)
  - `font-weight: 500`
- **"已完成(3)"** (Completed, 3) — Inactive:
  - Gray `#999` text color
  - No bottom border

Clicking a tab switches the active state (updates text color and bottom border). For this prototype, both tabs can show the same card list or "已完成" can show a different set — keep it simple: show 3 cards under "待完成", and a "暂无已完成练习" (No completed exercises yet) placeholder under "已完成".

### 1.3 Practice Task Cards

3 cards stacked vertically, `gap: 12px`, inside a scrollable area (`flex: 1`, `overflow-y: auto`, `padding: 16px`). Each card:

**Card structure:**
- White background, `border-radius: 8px`, `padding: 16px`, `1px solid #e8e5e0`
- **Title**: "氧化还原反应 — 基础练习" (or variations), `16px`, bold, Oxford Blue `#002045`, Cormorant Garamond
- **Tag row** (`margin-top: 8px`, `display: flex`, `gap: 6px`):
  - Small chips: `font-size: 12px`, `padding: 2px 10px`, `border-radius: 16px`
  - Subject tag: light blue `#e3f2fd` background, text `#1565c0`
  - Difficulty tag: same blue style
  - Card 1: [选择题] [中等难度]
  - Card 2: [填空题] [简单难度]
  - Card 3: [选择题] [困难难度]
- **Progress bar** (`margin-top: 12px`, `display: flex`, `align-items: center`, `gap: 10px`):
  - Bar track: `flex: 1`, `height: 6px`, `border-radius: 3px`, `background: #e0e0e0`
  - Bar fill: Oxford Blue `#002045`, `height: 100%`, `border-radius: 3px`, width set via inline style
  - Text: `font-size: 12px`, gray `#888`, e.g., "3/5"
- **"继续练习" (Continue) button** (`margin-top: 12px`):
  - Full width, `height: 40px`, Oxford Blue `#002045` background, white text
  - `border-radius: 8px`, `font-size: 14px`, `font-weight: 500`, `border: none`, `cursor: pointer`
  - Hover: `background: #003060`
  - **Clicking this button switches to View 2 (Quiz Interface)**

Card data:

| # | Title                              | Tags            | Progress |
|---|------------------------------------|-----------------|----------|
| 1 | 氧化还原反应 — 基础练习             | 选择题, 中等难度 | 3/5 (60%) |
| 2 | 离子反应方程式 — 专项训练            | 填空题, 简单难度 | 1/8 (12%) |
| 3 | 化学平衡与勒夏特列原理 — 综合练习    | 选择题, 困难难度 | 0/6 (0%)   |

---

## View 2 — Quiz Interface (Default Hidden)

### 2.1 Top Title Bar

`height: 56px`, Oxford Blue `#002045` background, `display: flex`, `align-items: center`, `padding: 0 12px`:

- **Left — Back arrow**: Unicode `←`, white, `20px`, `cursor: pointer`. Clicking returns to View 1.
- **Center — Title**: "练习" (Practice), `16px`, bold, white, `position: absolute`, `left: 50%`, `transform: translateX(-50%)`
- **Right section** (`margin-left: auto`, `display: flex`, `gap: 16px`, `align-items: center`):
  - **Countdown timer**: "25:30", `13px`, white, monospace font (IBM Plex Sans is fine). This is static text — no actual timer needed, but styling should suggest a live countdown.
  - **Question number**: "3/10", `13px`, white

### 2.2 Question Content Area

`flex: 1`, `overflow-y: auto`, `padding: 20px`:

#### Question Stem
- `font-size: 15px`, IBM Plex Sans, `color: #1a1a1a`, `line-height: 1.7`, `margin-bottom: 24px`
- The question text: "在氧化还原反应 2Fe + 3Cl₂ → 2FeCl₃ 中，氧化剂是？"
- Use Unicode subscript/superscript where possible, or just render the chemical formulas inline with clear formatting
- Bold the key phrase "氧化剂是？" for emphasis

#### 4 Option Buttons

Each option is a full-width button:

- `width: 100%`, `height: 56px`
- `background: white`, `border: 1px solid #ddd`, `border-radius: 8px`
- `margin-bottom: 8px`
- `display: flex`, `align-items: center`, `padding: 0 16px`
- `font-size: 15px`, IBM Plex Sans, `color: #333`
- `cursor: pointer`
- `transition: background 0.2s, border-color 0.2s`
- Default hover: border color darkens to `#bbb`

**Left — Option letter badge:**
- `28px` diameter circle, `border-radius: 50%`
- Background `#f0f0f0`, text color `#555`
- `font-size: 13px`, bold, centered
- `margin-right: 12px`, `flex-shrink: 0`
- Letter: A, B, C, D

**Option text:**

| Letter | Content                    | Is Correct? |
|--------|---------------------------|-------------|
| A      | Fe                        | No          |
| B      | Cl₂                       | **Yes**     |
| C      | FeCl₃                     | No          |
| D      | 以上都是                   | No          |

**Click behavior (JavaScript):**
- When user clicks an option:
  1. If it's the correct answer (B in this case): change its background to `#e0f2f1`, border to `#2c6e49`. Change its letter badge background to `#2c6e49`, text to white. Add a small ✓ checkmark to the right of the option text.
  2. If it's a wrong answer: change its background to `#ffdad6`, border to `#c0392b`. Change its letter badge background to `#c0392b`, text to white. Add a small ✗ mark to the right.
  3. If the user clicked a wrong answer, also briefly highlight the correct answer (B) with a green border pulse or simply reveal it immediately — **show the correct answer after 0.3s delay**.
  4. Once an option is clicked, **all options become non-clickable** (pointer-events: none or a flag).
  5. The transition to colored states should use `transition: background 0.3s, border-color 0.3s`.

### 2.3 Bottom Navigation Buttons

`padding: 12px 20px`, `background: white`, `border-top: 1px solid #eee`, `display: flex`, `justify-content: space-between`, `gap: 12px`:

- **"上一题" (Previous) button**:
  - `flex: 1`, `height: 44px`
  - `background: #f0f0f0`, text color `#666`
  - `border: 1px solid #ddd`, `border-radius: 8px`
  - `font-size: 14px`, IBM Plex Sans, `cursor: pointer`
  - Left arrow `‹` or `←` before the text
  - Disabled state when on question 1: `opacity: 0.4`, `pointer-events: none`
  - Hover: `background: #e8e8e8`

- **"下一题" (Next) button**:
  - `flex: 1`, `height: 44px`
  - Oxford Blue `#002045` background, white text
  - `border: none`, `border-radius: 8px`
  - `font-size: 14px`, IBM Plex Sans, `cursor: pointer`
  - Right arrow `›` or `→` after the text
  - Hover: `background: #003060`
  - Clicking advances to the next question — for this prototype, just show a subtle visual feedback (brief flash or just acknowledge the click — no actual content change needed)

---

## JavaScript Requirements

All vanilla JS — no frameworks, no libraries.

### View Switching:
1. Clicking "继续练习" (Continue) on any task card in View 1 → hides View 1 (`display: none`), shows View 2 (`display: flex` for the quiz container).
2. Clicking the back arrow (`←`) in View 2's top bar → hides View 2, shows View 1.
3. Both views are top-level siblings in the DOM, toggled via JS.

### Task List Tab Switching:
1. Clicking "待完成(7)" → set it active (Oxford Blue text + bottom border), "已完成(3)" inactive (gray).
2. Clicking "已完成(3)" → reverse. When "已完成" is active, show placeholder text "暂无已完成练习" instead of the task cards.

### Option Button Click (View 2):
1. On first click of any option:
   - Determine if correct (option B = correct).
   - If correct: apply green styles (bg `#e0f2f1`, border `#2c6e49`, badge bg `#2c6e49` white text, ✓ mark).
   - If wrong: apply red styles to clicked option (bg `#ffdad6`, border `#c0392b`, badge bg `#c0392b` white text, ✗ mark). After `0.3s` delay (`setTimeout`), apply green styles to the correct option (B).
   - Set a flag so subsequent clicks are ignored.
2. The ✓ and ✗ marks can be small Unicode characters added via JS (`textContent` appended) or separate `<span>` elements toggled.

### Bottom Tab Bar:
1. "练习" tab is active (Oxford Blue). Other tabs are inactive (gray). Clicking other tabs updates the visual state for the prototype (no actual navigation).

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond (400, 700) and IBM Plex Sans (400, 500) via a `<link>` in `<head>`.
- **Global box-sizing**: `border-box`.
- **Body styling**: `margin: 0`, `padding: 0`, `background: #e8e5e0`.
- **Container**: `max-width: 390px`, `margin: 0 auto`, `min-height: 100vh`, `background: #faf8f5`, `position: relative`, `display: flex`, `flex-direction: column`.
- **Icons**: Unicode characters only (←/→ arrows, ✓ checkmark, ✗ cross, 💬📝❌👤 for tabs). No icon libraries.
- **No images**: all visuals are CSS shapes, text, colored divs.
- **Content area**: both views use `flex: 1` for the scrollable content area, with the bottom tab bar fixed at the bottom. View 2 also accounts for the navigation buttons above the tab bar.
- **View 1 content** needs `padding-bottom: 70px` to clear the bottom tab bar.
- **View 2 layout**: title bar → question content (flex: 1, overflow-y: auto) → nav buttons → tab bar.
- **Smooth transitions**: view switch (optional fade), option button color changes (0.3s), button hovers, tab state changes.
- **Mobile feel**: clean quiz interface, clear feedback on answer selection, intuitive navigation.

---

## Visual Structure Summary

### View 1 — Task List
```
┌──────────────────────────────────────┐
│  ←          练习           3/10      │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────┤
│  ───待完成(7)───────已完成(3)───      │ ← Sub-tabs (44px)
│       ████                            │   Blue underline on active
├──────────────────────────────────────┤
│  ┌──────────────────────────────┐    │
│  │ 氧化还原反应 — 基础练习       │    │
│  │ [选择题] [中等难度]           │    │ ← Tags
│  │ ██████████░░░░░░  3/5        │    │ ← Progress bar
│  │ ┌──────────────────────────┐ │    │
│  │ │       继续练习            │ │    │ ← Oxford Blue button
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 离子反应方程式 — 专项训练     │    │
│  │ [填空题] [简单难度]           │    │
│  │ ██░░░░░░░░░░░░░░  1/8        │    │
│  │ ┌──────────────────────────┐ │    │
│  │ │       继续练习            │ │    │
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 化学平衡 — 综合练习           │    │
│  │ [选择题] [困难难度]           │    │
│  │ ░░░░░░░░░░░░░░░░  0/6        │    │
│  │ ┌──────────────────────────┐ │    │
│  │ │       继续练习            │ │    │
│  │ └──────────────────────────┘ │    │
│  └──────────────────────────────┘    │
├──────────────────────────────────────┤
│   💬       📝       ❌       👤       │ ← Tab bar (56px)
│  AI助教    练习     错题     我的      │   "练习" active
└──────────────────────────────────────┘
```

### View 2 — Quiz Interface
```
┌──────────────────────────────────────┐
│  ←          练习      25:30   3/10   │ ← Top bar (56px, Oxford Blue)
├──────────────────────────────────────┤
│                                      │
│  在氧化还原反应                       │
│  2Fe + 3Cl₂ → 2FeCl₃ 中，           │ ← Question stem
│  氧化剂是？                           │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ (A)  Fe                      │    │ ← Option (white, default)
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ (B)  Cl₂                  ✓  │    │ ← Correct (green after click)
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ (C)  FeCl₃                ✗  │    │ ← Wrong if clicked (red)
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ (D)  以上都是                  │    │
│  └──────────────────────────────┘    │
│                                      │
├──────────────────────────────────────┤
│  [  ‹ 上一题  ]    [  下一题 ›  ]    │ ← Nav buttons
├──────────────────────────────────────┤
│   💬       📝       ❌       👤       │ ← Tab bar (56px)
│  AI助教    练习     错题     我的      │
└──────────────────────────────────────┘
```
