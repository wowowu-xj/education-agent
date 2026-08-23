Generate a single self-contained HTML file for a teacher-facing AI Agent conversation panel. Use Tailwind CSS CDN (`<script src="https://cdn.tailwindcss.com"></script>`) and configure the custom colors below. No build tools, no framework except vanilla HTML/CSS/JS.

## LAYOUT

Desktop viewport 1280px+. Flexbox layout: left fixed 240px sidebar + right fluid conversation area.

```
┌──────────┬──────────────────────────────────────────────┐
│ Sidebar  │ Context Tags Bar                             │
│ 240px    ├──────────────────────────────────────────────┤
│ fixed    │ Message List (scrollable, flex-grow)         │
│          │  - User bubble (right-aligned)               │
│          │  - AI bubble (left-aligned)                  │
│          │  - Tool call card                            │
│          ├──────────────────────────────────────────────┤
│          │ Quick Chips (6 preset prompt buttons)        │
│          ├──────────────────────────────────────────────┤
│          │ Chemistry Formula Shortcut Bar               │
│          ├──────────────────────────────────────────────┤
│          │ Input Area (textarea + attach + send button) │
│          ├──────────────────────────────────────────────┤
│          │ Agent Status Bar ("Ready")                   │
└──────────┴──────────────────────────────────────────────┘
```

## DESIGN TOKENS

Configure Tailwind with these exact custom colors:

```js
tailwind.config = {
  theme: {
    extend: {
      colors: {
        oxford: '#002045',       // primary: buttons, sidebar, titles
        teal: '#13696a',         // accent: AI buttons, AI bubbles, chemical emphasis
        'teal-light': '#e0f2f1', // AI chat bubble background
        'warm-paper': '#faf8f5', // main content background
        'sidebar-bg': '#1a1a2e', // sidebar dark background
        'text-body': '#1a1a2e',  // body text
        'text-secondary': '#6b7280', // secondary text, timestamps
        'bubble-user-border': '#d1d5db', // user bubble border
        'card-hover': '#f9fafb', // hover state
      },
      fontFamily: {
        heading: ['Cormorant Garamond', 'serif'],
        body: ['IBM Plex Sans', 'Noto Sans SC', 'sans-serif'],
      },
      borderRadius: {
        'card': '8px',
        'bubble': '12px',
        'chip': '16px',
      }
    }
  }
}
```

Include these Google Fonts via CDN:
- Cormorant Garamond (400, 600, 700)
- IBM Plex Sans (400, 500)
- Noto Sans SC (400, 500) — as Chinese fallback

## COMPONENT 1: SIDEBAR (240px, fixed left, full height)

- Background: `#1a1a2e` (sidebar-bg)
- Top: Logo area — "ChemAI" in Cormorant Garamond, white, 24px bold, with "智辅化学" below in IBM Plex Sans, text-secondary, 14px
- Below logo: a "New Conversation" button — full width (minus 16px horizontal padding), Teal `#13696a` background, white text, 40px height, rounded 8px, centered text "+ 新建对话"
- Conversation history list (5 mock items):
  - Each item: a clickable row with conversation title (white, 14px, single line truncate) + timestamp below (text-secondary, 12px)
  - The 5 titles: "氧化还原反应专题出题", "高一3班月考成绩分析", "离子方程式配平练习", "化学平衡教学设计", "元素周期律复习资料"
  - Timestamps: "2分钟前", "1小时前", "昨天 14:30", "昨天 10:15", "3天前"
  - Active item (first one): left 3px Teal indicator bar, slightly lighter background `rgba(19,105,106,0.15)`
- Bottom: 4 navigation icon buttons in a horizontal row — 首页, 工作台, 学情, 设置 — use simple SVG icons (home, grid, chart, gear) in text-secondary, 20px, with Chinese labels below in 11px text-secondary. Equal spacing. Add a thin top border separating them from the history list.

## COMPONENT 2: CONTEXT TAGS BAR (top of conversation area)

- Background: white `#ffffff`, bottom border `1px solid #e5e7eb`
- Height: ~44px, padding: 8px 20px
- Shows a tag chip: "当前班级：高一(3)班" — light warm background, oxford text, 13px, rounded 16px chip
- Next to it: "+ 选择上下文" in text-secondary, 13px, clickable style

## COMPONENT 3: MESSAGE LIST (scrollable, flex-grow, padding 24px)

Background: warm-paper `#faf8f5`. Display 4 messages in chronological order:

### Message 1 — User bubble (right-aligned)
- White background `#ffffff`, 1px solid `#d1d5db` border, rounded 12px (top-right 4px for speech tail effect)
- Max-width: 65% of container
- Text: "帮我出3道关于氧化还原反应的选择题，难度中等，给高一学生用"
- Text color: text-body `#1a1a2e`, 15px, line-height 1.6
- Right-aligned using `margin-left: auto`

### Message 2 — AI bubble (left-aligned)
- Teal-light `#e0f2f1` background, no border, rounded 12px (top-left 4px)
- Max-width: 65%
- Text: "好的，我来为你生成3道氧化还原反应选择题。请稍等，我先检索相关知识点和历年真题..."
- Text color: text-body, 15px, line-height 1.6

### Message 3 — Tool Call Card (embedded in message flow, left-aligned)
- A distinct card with left 4px Teal border, white background, rounded 8px, subtle shadow
- Header row: tool icon (wrench SVG, 16px) + "🔧 工具调用：search_question_bank" in text-secondary 13px + elapsed timer "⏱ 2.3s" on the right
- Body: JSON-like parameter summary in a light gray `#f3f4f6` code block, monospace 13px:
  ```
  topic: "氧化还原反应"
  type: ["选择题"]
  difficulty: "medium"
  count: 3
  grade: "高一"
  ```
- Below: a thin progress bar (6px height, gray track, Teal fill at ~60%, subtle pulse animation) with label "检索中..."

### Message 4 — AI bubble with formatted result (left-aligned)
- Same Teal-light background as Message 2
- Contains a structured response:
  - Title: "✅ 已生成 3 道氧化还原反应选择题" in bold 16px oxford color
  - Three question previews, each in a mini card: white background, rounded 8px, 1px border `#e5e7eb`, padding 12px, margin-bottom 8px
  - Each mini card shows: question number badge (oxford circle, white number, 20px) + truncated question text (2 lines max) + difficulty chip (中等 = yellow-tinted bg with brown text)
  - Below questions: "题目已加入出题工作台，可前往审核" in text-secondary 13px italic

## COMPONENT 4: QUICK CHIPS (6 preset prompt buttons)

- Positioned above the input area, padding 12px 20px
- Horizontal row, flex-wrap allowed, gap 8px
- 6 chip buttons:
  1. "⚡ 出3道氧化还原题"
  2. "📊 分析班级月考成绩"
  3. "📝 最近考试错题统计"
  4. "📖 生成知识点总结"
  5. "💡 推荐教学策略"
  6. "🔍 查看学生薄弱点"
- Each chip: white background `#ffffff`, 1px solid `#d1d5db` border, rounded 16px, padding 6px 14px, text-body 13px, cursor pointer
- Hover: border turns Teal, background shifts to `#e0f2f1` very slightly, subtle scale 1.02 transition

## COMPONENT 5: CHEMISTRY FORMULA SHORTCUT BAR

- Positioned above the input area, below quick chips
- Horizontal row of 8 formula shortcut buttons, padding 8px 20px, gap 6px
- Each button: white background, 1px solid `#e5e7eb`, rounded 6px, padding 4px 10px, monospace 14px, text-secondary
- Buttons:
  1. "H₂O" (subscript rendered correctly)
  2. "→" (arrow)
  3. "↑" (up arrow / gas)
  4. "↓" (down arrow / precipitate)
  5. "Δ" (delta / heat)
  6. "⇌" (equilibrium arrow)
  7. "²⁻" (superscript minus)
  8. "³⁺" (superscript plus)
- Hover: oxford border, oxford text color
- Click: appends symbol to textarea cursor position (just show visual, no JS implementation needed for static mock)

## COMPONENT 6: INPUT AREA (bottom of conversation area)

- White background `#ffffff`, top border `1px solid #e5e7eb`, padding 12px 20px
- Flex row: attach icon button (left) + textarea (flex-grow, center) + send button (right)
- **Attach icon button**: 36px circle, text-secondary, paperclip SVG icon (16px), hover bg `#f3f4f6`, cursor pointer
- **Textarea**: flex-grow, min-height 44px, max-height 120px, no border, no outline, placeholder "输入消息... (支持化学式 \ce{...} 语法)", text-body 15px, line-height 1.5, resize none. Focus: no visible ring (clean look).
- **Send button**: 40px circle, Oxford Blue `#002045` background, white upward-arrow SVG icon (18px). Hover: darken to `#001a30`. Subtle shadow. Disabled state: opacity 50% (show this as default, since textarea is empty).

## COMPONENT 7: AGENT STATUS BAR (below input area)

- Thin bar, height ~28px, background `#f3f4f6`, padding 4px 20px
- Left side: status indicator dot (8px circle, green `#22c55e` for "ready") + "就绪" text in text-secondary 12px
- Right side: "ChemAI Agent v1.0" in text-secondary 11px

## INTERACTION DETAILS (CSS-only where possible, minimal JS)

1. Sidebar conversation history items: hover shows lighter background, cursor pointer
2. Quick chips: hover border turns Teal with smooth 0.2s transition
3. Send button: show disabled state (opacity 0.5). Add a small JS snippet that enables it when textarea is non-empty, disables when empty. Use `input` event listener on textarea.
4. Message area: auto-scroll to bottom on page load (simple JS `scrollTop = scrollHeight` on the message container)
5. Smooth scroll behavior on the message list container

## IMPORTANT CONSTRAINTS

- All data is STATIC mock data. No API calls. No fetch(). No network requests.
- The page is a teacher-facing DESKTOP tool. Do NOT add mobile responsive breakpoints — design for 1280px+ only.
- Sidebar and input area must use `position: sticky` or `fixed` appropriately so the sidebar stays visible and the input area stays at bottom while scrolling messages.
- Use semantic HTML5 tags (aside, main, section, header, footer).
- Add proper `alt` text on all SVG icons.
- The overall feel should be professional, calm, and academic — like a university research tool, not a consumer chat app.
- Do NOT include any Vue, React, or other framework code. Pure HTML + Tailwind CDN + minimal vanilla JS.

Output ONLY the complete HTML file, starting with `<!DOCTYPE html>`. No explanations, no markdown fences around the code — just the raw HTML ready to save as index.html and open in a browser.
