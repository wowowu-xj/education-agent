# Google Stitch Prompt: Teacher Student Management (students.html)

---

Generate a single, self-contained HTML file (`students.html`) for a teacher's student management page. Use **vanilla HTML + CSS + JavaScript** — no frameworks, no libraries. All CSS, JS, and HTML in one file.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Background**: warm paper `#faf8f5`
- **Card background**: white `#ffffff`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Cards `8px`, Buttons `8px`, Chips `16px`, Search input `8px`
- **Card styling**: white background, `1px solid #e8e5e0`, `border-radius: 8px`, padding `16px`, subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- **Obstacle segment colors**:
  - 概念 (Concept): Purple `#7b4fbf`
  - 审题 (Exam Reading): Blue `#3b82f6`
  - 表述 (Expression): Cyan `#0891b2`
- **Score dot colors**:
  - Good (≥75): Green `#2e7d32`
  - Warning (60–74): Amber `#e6a817`
  - Poor (<60): Red `#c62828`
- **Target viewport**: Desktop 1280px+

The entire page uses `max-width: 1280px`, centered with `margin: 0 auto`, padding `32px`.

---

## Page Layout (Top to Bottom)

### 1. Top Statistics Bar

A horizontal flexbox row with **4 stat items** evenly spaced. Each stat item:

- **Small label** on top: `12px`, gray `#888`, IBM Plex Sans
- **Large number** below: Oxford Blue `#002045`, `24px`, `bold`, IBM Plex Sans, `2px` margin-top

Stat data:

| Label        | Value |
|--------------|-------|
| 总人数       | 42    |
| 活跃学生     | 38    |
| 关注学生     | 5     |
| 班级平均     | 78.5  |

Add subtle vertical dividers (`1px solid #e8e5e0`, `height: 40px`) between the stat items. The stats bar sits on a white card background with `16px` padding and `8px` border-radius.

### 2. Search & Filter Bar

A white card containing:

#### Search Input
A **full-width text input** with:
- Placeholder: "搜索学生姓名..." (Search student name...)
- Search icon (🔍 or inline SVG magnifying glass) on the left side, positioned inside the input or in a wrapper
- `border-radius: 8px`, `1px solid #d5d0c8` border, `12px 16px` padding, IBM Plex Sans
- Light `#faf8f5` background, focus state with Oxford Blue border

#### Filter Chips Row
Below the search input (or on the same row if space allows), a row of **filter chips** (`border-radius: 16px`). Each chip is a pill-shaped button/label:

- **班级 (Class)**: a group of chips — 全部 (All, active by default), 高一(3)班, 高一(4)班
- **障碍类型 (Obstacle Type)**: — 全部 (All, active), 概念, 审题, 表述
- **活跃状态 (Status)**: — 全部 (All, active), 活跃, 不活跃

Chip styling:
- Default: light gray `#f0ede8` background, gray `#666` text, `1px solid #e8e5e0`
- Active/selected: Oxford Blue `#002045` background, white text, no border
- `padding: 6px 16px`, `font-size: 13px`, `border-radius: 16px`, cursor pointer
- Clicking a chip toggles its active state (JavaScript class toggle)

### 3. Student Card Grid (3 Columns)

A **CSS Grid**: `grid-template-columns: repeat(3, 1fr)`, `gap: 16px`. Display **6 student cards** (2 rows × 3 columns).

Each student card contains (top to bottom):

1. **Avatar + Name row** (flexbox, align-items center):
   - **Avatar placeholder**: `40px` circle, gray `#d5d0c8` background, white centered initials in `14px` bold (e.g., "张", "李", "王", "赵", "陈", "刘")
   - **Name**: `16px`, bold, Oxford Blue `#002045`, Cormorant Garamond, `8px` left margin
   
2. **Class tag**: small gray `12px` text below the name, e.g., "高一(3)班"

3. **Obstacle distribution bar**: a thin horizontal segmented bar, full width of card, `height: 4px`, `border-radius: 2px`. Three colored segments laid out horizontally using flexbox or inline divs. The width of each segment is proportional to the student's obstacle profile:
   - Purple segment (#7b4fbf) = 概念障碍
   - Blue segment (#3b82f6) = 审题障碍
   - Cyan segment (#0891b2) = 表述障碍
   
   Total always sums to 100% width. Below the bar, a tiny legend row showing the 3 colors as 8px dots with abbreviated labels.

4. **Recent score trend dots**: a row of **3 small circles** (`12px` diameter), `4px` gap, showing the last 3 test results:
   - Green `#2e7d32` = ≥75
   - Amber `#e6a817` = 60–74
   - Red `#c62828` = <60

5. **"详情" (Details) button**: Teal `#13696a` background, white text, small size (`padding: 6px 20px`, `font-size: 13px`), `border-radius: 8px`, aligned to the right side of the card. On click, opens the detail drawer for that student. Subtle hover effect (slightly darker teal).

Student card data:

| # | Name | Class     | Obstacle Distribution (概念/审题/表述) | Recent Scores (dots) |
|---|------|-----------|--------------------------------------|----------------------|
| 1 | 张明 | 高一(3)班 | 50% / 30% / 20%                     | 🟢 🟡 🔴 (78, 65, 52)   |
| 2 | 李华 | 高一(3)班 | 20% / 60% / 20%                     | 🟡 🔴 🟢 (62, 48, 76)   |
| 3 | 王芳 | 高一(3)班 | 10% / 20% / 70%                     | 🟢 🟢 🟡 (82, 75, 68)   |
| 4 | 赵磊 | 高一(3)班 | 60% / 20% / 20%                     | 🔴 🔴 🟡 (45, 52, 63)   |
| 5 | 陈静 | 高一(3)班 | 30% / 50% / 20%                     | 🟢 🟡 🟡 (80, 67, 64)   |
| 6 | 刘洋 | 高一(3)班 | 20% / 30% / 50%                     | 🟡 🟢 🟢 (70, 77, 85)   |

### 4. Right Detail Drawer (Slide-out Panel)

A **fixed-position drawer** (`position: fixed`, `top: 0`, `right: 0`, `height: 100vh`, `width: 480px`):

- **Default state**: `right: -480px` (hidden off-screen), `transition: right 0.3s ease`
- **Open state**: `right: 0` (slides in), triggered by clicking a card's "详情" button
- **Close**: clicking the overlay, or a close (✕) button in the top-right corner of the drawer
- **Overlay**: full-screen semi-transparent black background `rgba(0,0,0,0.4)`, `position: fixed`, `inset: 0`, `z-index` below the drawer but above page content. Clicking the overlay closes the drawer. The overlay fades in/out with `opacity` transition.
- **Drawer z-index**: above the overlay

#### Drawer Content (scrollable, `overflow-y: auto`, padding `24px`)

**1. Student Basic Info Section:**
- Large avatar placeholder: `64px` circle, gray `#d5d0c8`, white initials `24px`
- Name: Cormorant Garamond, `22px`, bold, Oxford Blue
- 学号 (Student ID): gray `14px`, e.g., "G20240301"
- 班级 (Class): gray `14px`, e.g., "高一(3)班"
- A subtle horizontal divider (`1px solid #e8e5e0`)

**2. Obstacle Distribution Section:**
- Section title: "障碍类型分布" (Obstacle Type Distribution), `16px`, bold, Oxford Blue
- Three horizontal bars, each full width of the drawer content area:
  - Label on the left (`width: 80px`, `font-size: 13px`), colored segment bar in the middle, percentage on the right
  - Bar track: `height: 10px`, `border-radius: 5px`, gray `#e8e5e0` background
  - Filled segment: corresponding obstacle color, `border-radius: 5px`, width set via inline style
  - Purple bar: 概念理解障碍 — 50%
  - Blue bar: 审题障碍 — 30%
  - Cyan bar: 表述障碍 — 20%

**3. Score Trend Mini Line Chart:**
- Section title: "近期成绩趋势" (Recent Score Trend), `16px`, bold, Oxford Blue
- Chart area: `height: 180px`, light `#f5f3ef` background, `border-radius: 8px`, relative-positioned
- Y-axis: 0 to 100, with light grid lines at 20, 40, 60, 80
- X-axis: 6 test labels (测试1 through 测试6)
- Data points: `8px` circles, Oxford Blue `#002045`, absolutely positioned
- Connect points with thin `2px` Oxford Blue lines using inline SVG `<polyline>` or absolutely positioned rotated divs
- Sample data: 测试1=55, 测试2=62, 测试3=48, 测试4=70, 测试5=65, 测试6=78
- Show the score value as a small label above each point

**4. Weak Knowledge Points Tag List:**
- Section title: "薄弱知识点" (Weak Knowledge Points), `16px`, bold, Oxford Blue
- A flexbox-wrapped row of tags/chips:
  - 氧化还原反应 (Redox Reactions) — red tint `#ffdad6`, text `#93000a`
  - 离子方程式 (Ionic Equations) — orange tint `#fff3cd`, text `#856404`
  - 化学平衡 (Chemical Equilibrium) — orange tint `#fff3cd`, text `#856404`
  - 电化学 (Electrochemistry) — red tint `#ffdad6`, text `#93000a`
- Each tag: `border-radius: 16px`, `padding: 4px 14px`, `font-size: 13px`

**5. Action Button Group:**
Three buttons in a row at the bottom of the drawer, equal width, `8px` gap:
- **"生成学习计划"** (Generate Study Plan): Oxford Blue `#002045` background, white text
- **"发送通知"** (Send Notification): white background, `1px solid #002045`, Oxford Blue text (outline style)
- **"编辑信息"** (Edit Info): white background, `1px solid #d5d0c8`, gray text (subtle outline)
- Each button: `border-radius: 8px`, `padding: 10px 0`, `font-size: 14px`, `cursor: pointer`, full width within its flex column

### 5. Bottom Pagination

A centered pagination control at the bottom of the page, `margin-top: 32px`:

- Flexbox row, `justify-content: center`, `align-items: center`, `gap: 8px`
- **"上一页" (Previous)** button on the left: light gray background, gray text, disabled state (opacity 0.4) when on page 1
- **Page number buttons** (1 through 8): `36px` × `36px` squares, `border-radius: 8px`, `font-size: 14px`
  - Current page (page 1): Oxford Blue `#002045` background, white text
  - Other pages: white background, `1px solid #e8e5e0`, gray text, hover effect (light blue tint)
  - Show ellipsis "…" between page 5 and page 8 if needed for realism
- **"下一页" (Next)** button on the right: Oxford Blue `#002045` background, white text
- Clicking a page number updates the active state (JavaScript class toggle)

---

## JavaScript Requirements

All JavaScript must be **vanilla JS** — no frameworks, no libraries.

### Drawer Behavior:
1. Clicking any card's "详情" button:
   - Populate the drawer with that student's data (update name, avatar initial, student ID, obstacle bars, score chart, weak knowledge tags — or use a single static drawer with sample data for simplicity; pick the simpler approach: **static drawer content, same for all cards**)
   - Add the `.open` class to the drawer (`right: 0`)
   - Show the overlay (`opacity: 1`, `pointer-events: auto`)
2. Clicking the close (✕) button:
   - Remove the `.open` class from the drawer (`right: -480px`)
   - Hide the overlay (`opacity: 0`, `pointer-events: none`)
3. Clicking the overlay:
   - Same close behavior as the close button
4. Pressing the `Escape` key:
   - Same close behavior

### Filter Chip Behavior:
- Clicking a chip in a group deselects siblings in the same group and selects the clicked one (single-select within each filter category)
- "全部" (All) chips are selected by default

### Pagination Behavior:
- Clicking a page number updates which page number has the active style
- Clicking "上一页" (Previous) decrements the active page (min 1)
- Clicking "下一页" (Next) increments the active page (max 8)
- No actual data loading — just visual state change

---

## CSS / Implementation Notes

- **Single file output**: all HTML, CSS, and JS in one file.
- **Google Fonts**: load Cormorant Garamond and IBM Plex Sans via a `<link>` in `<head>`.
- **Icons**: use Unicode symbols (🔍 for search, ✕ for close, ✓ for check) or simple inline SVGs. No icon libraries.
- **No images**: avatar placeholders are CSS circles with centered text initials.
- **Section spacing**: `24px` vertical gap between major sections.
- **Page heading**: "学生管理" (Student Management) as the page title at the very top, Cormorant Garamond, `28px`, bold, Oxford Blue `#002045`.
- **Smooth transitions**: use CSS `transition` for the drawer slide, overlay fade, button hovers, and chip state changes.
- **Scrollbar**: the drawer content scrollbar should be thin and subtle (`::-webkit-scrollbar` custom styling).
- The overall feel should be clean, organized, and professional — an efficient student management tool for a dedicated teacher.

---

## Visual Structure Summary

```
┌──────────────────────────────────────────────────────────────┐
│  学生管理                                                     │
├──────────┬──────────┬──────────┬──────────────────────────────┤
│  总人数   │ 活跃学生  │ 关注学生  │  班级平均                     │
│   42     │   38     │    5     │   78.5                       │
├──────────┴──────────┴──────────┴──────────────────────────────┤
│  🔍 搜索学生姓名...                                            │
│  [全部] [高一3班] [高一4班] | [全部] [概念] [审题] [表述] | [全部] [活跃] [不活跃] │
├─────────────────┬─────────────────┬──────────────────────────┤
│  👤 张明         │  👤 李华         │  👤 王芳                   │
│  高一(3)班       │  高一(3)班       │  高一(3)班                 │
│  ████░░ 概念/审题 │  ██░░██ 概念/审题 │  █░░░██ 概念/审题          │
│  ● ● ● (趋势)    │  ● ● ● (趋势)    │  ● ● ● (趋势)              │
│         [详情]   │         [详情]   │         [详情]             │
├─────────────────┼─────────────────┼──────────────────────────┤
│  👤 赵磊         │  👤 陈静         │  👤 刘洋                   │
│  高一(3)班       │  高一(3)班       │  高一(3)班                 │
│  ███░░░ 概念/审题 │  ██░██░ 概念/审题 │  █░██░█ 概念/审题          │
│  ● ● ● (趋势)    │  ● ● ● (趋势)    │  ● ● ● (趋势)              │
│         [详情]   │         [详情]   │         [详情]             │
├─────────────────┴─────────────────┴──────────────────────────┤
│              [上一页]  1 2 3 ... 8  [下一页]                    │
└──────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │  ✕  学生详情          │
                    │                      │
                    │  👤 张明              │
                    │  学号: G20240301      │
                    │  班级: 高一(3)班       │
                    │  ─────────────────   │
                    │  障碍类型分布          │
                    │  概念 ████████ 50%    │
                    │  审题 ██████░░ 30%    │
                    │  表述 ████░░░░ 20%    │
                    │  ─────────────────   │
                    │  近期成绩趋势          │
                    │  80┤    ●            │
                    │  60┤  ●   ● ●        │
                    │  40┤●                │
                    │    └─┴─┴─┴─┴─┴─      │
                    │  ─────────────────   │
                    │  薄弱知识点            │
                    │  [氧化还原] [离子方程式] │
                    │  [化学平衡] [电化学]    │
                    │  ─────────────────   │
                    │  [生成学习计划]         │
                    │  [发送通知]            │
                    │  [编辑信息]            │
                    └──────────────────────┘
```
