# Google Stitch Prompt: Student Login Page (m/login.html)

---

Generate a single, self-contained HTML file (`m/login.html`) for a student mobile login page. Use **vanilla HTML + CSS only** — no frameworks, no libraries. All CSS and HTML in one file. This page has no JavaScript interaction beyond a simple password visibility toggle.

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Background**: warm paper `#faf8f5`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Inputs `8px`, Button `8px`
- **Target viewport**: Mobile — `max-width: 390px`, `min-height: 844px`, centered on screen with `margin: 0 auto`. The outer page background is `#faf8f5`.

---

## Page Container

The entire page content is wrapped in a single container:

```css
.container {
  max-width: 390px;
  min-height: 844px;
  margin: 0 auto;
  background: #faf8f5;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}
```

This centers all content vertically and horizontally within the mobile viewport.

---

## Component 1 — Logo Area

A centered flexbox column, `margin-bottom: 40px`, `text-align: center`.

### Chemistry Flask Graphic (Pure CSS)

A simplified chemistry flask drawn entirely with CSS (no images, no SVG). Build it using nested `<div>` elements with `border` and `border-radius`:

**Flask structure (container 100×100px, centered):**

- **Bowl (round bottom)**: a `<div>` with `width: 56px`, `height: 56px`, `border: 3px solid #002045`, `border-radius: 50%`, positioned at the bottom portion of the container. Use `border-bottom` slightly thicker or rely on the full circle — the neck will overlap it.

- **Neck (tube)**: a `<div>` with `width: 20px`, `height: 36px`, `border-left: 3px solid #002045`, `border-right: 3px solid #002045`, positioned above the bowl, centered. No border-top or border-bottom — just the two side borders forming an open tube.

- **Rim (lip at top)**: a `<div>` with `width: 30px`, `height: 6px`, `border: 3px solid #002045`, `border-radius: 3px`, positioned at the very top of the flask.

- **Liquid fill** (optional decorative touch): a `<div>` inside the bowl, `width: 40px`, `height: 20px`, background Teal `#13696a` with `opacity: 0.3`, `border-radius: 0 0 50% 50%`, positioned at the bottom of the bowl. This gives a subtle "liquid inside" effect.

- **Bubble** (optional): a tiny `<div>`, `6px` diameter, `border-radius: 50%`, Teal `#13696a` with `opacity: 0.5`, absolutely positioned inside the liquid area.

Position everything using a relative container (`position: relative`, `width: 100px`, `height: 100px`, `margin: 0 auto`). Use absolute positioning for the bowl, neck, rim, liquid, and bubble.

### App Title

Below the flask, `margin-top: 16px`:

- **"ChemAI 智辅化学"**: Oxford Blue `#002045`, `24px`, bold, Cormorant Garamond, centered
- **"你的AI化学学习伙伴"** (Your AI Chemistry Learning Partner): gray `#888`, `14px`, IBM Plex Sans, `margin-top: 6px`, centered

---

## Component 2 — Login Form

A form container with `width: 320px`, `margin: 0 auto`. Use a plain `<div>` (no actual `<form>` submission needed — this is a static prototype).

### Student ID / Phone Input

- `<input type="text">`
- `width: 100%`, `height: 48px`
- `border-radius: 8px`
- `border: 1px solid #ddd`
- `padding: 0 14px`
- `font-size: 15px`, IBM Plex Sans
- `color: #333`
- Placeholder: `"请输入学号或手机号"` (Please enter student ID or phone number)
- `background: white`
- `box-sizing: border-box`
- **Focus state**: `border-color: #002045`, `box-shadow: 0 0 0 3px rgba(0,32,69,0.1)`, `outline: none`
- `margin-bottom: 16px`

### Password Input

- `<input type="password">` (default type is password to mask characters)
- Same dimensions and styling as the student ID input
- Placeholder: `"请输入密码"` (Please enter password)
- **Eye icon toggle** on the right side inside the input area:
  - Use a wrapper `<div>` with `position: relative` around the password input
  - A `<span>` with the Unicode character `👁` (or `👁️`) positioned absolutely on the right side (`right: 14px`, `top: 50%`, `transform: translateY(-50%)`, `cursor: pointer`, `font-size: 18px`, `color: #999`, `user-select: none`)
  - Clicking the eye toggles the input `type` between `password` and `text` (simple vanilla JS: `input.type = input.type === 'password' ? 'text' : 'password'`)
  - Also toggle the eye appearance: open eye `👁` = password visible, closed/slashed eye concept = password hidden. Use two Unicode characters: `👁` (show password, when type=text) and a slashed eye alternative. Simpler approach: just toggle between `👁` and `🙈` or use `👁` with opacity change (full opacity when password is visible, 0.4 opacity when hidden).

### Login Button

- Full-width button: `width: 320px`, `height: 48px`
- Oxford Blue `#002045` background
- White text, `font-size: 16px`, `font-weight: 500`, IBM Plex Sans
- `border-radius: 8px`
- `border: none`
- `cursor: pointer`
- `margin-top: 20px`
- Text: "登录" (Login)
- **Hover state**: `background: #1a365d` (a slightly lighter/different dark blue — use `#1a365d` as specified)
- **Active/press state**: `background: #001a35`, subtle scale `transform: scale(0.98)`
- Smooth transition: `transition: background 0.2s, transform 0.1s`

---

## Component 3 — Footer Text

Centered below the form, `margin-top: 32px`, `text-align: center`:

### Registration Link
- Text: "还没有账号？联系老师注册" (Don't have an account? Contact your teacher to register)
- `font-size: 14px`, IBM Plex Sans
- Color: gray `#999`
- The words "联系老师注册" should be styled as a link: underline, cursor pointer, color Oxford Blue `#002045` (or keep consistent gray with underline on hover)
- Hover: text color darkens

### Version Number
- Text: "v0.1.0"
- `font-size: 12px`, IBM Plex Sans
- Color: light gray `#bbb`
- `margin-top: 16px`
- Centered

---

## JavaScript

Minimal vanilla JS — only the password visibility toggle:

1. Click the eye icon → toggle the password input `type` between `password` and `text`.
2. Also toggle the eye icon appearance to give visual feedback (change Unicode character or opacity).

No other JavaScript is needed. This is a static login page prototype.

---

## CSS / Implementation Notes

- **Single file output**: all HTML and CSS in one file. JS inline in a `<script>` tag at the bottom.
- **Google Fonts**: load Cormorant Garamond (weights: 400, 700) and IBM Plex Sans (weights: 400, 500) via a `<link>` in `<head>`.
- **Box sizing**: use `* { box-sizing: border-box; }` globally to avoid padding/sizing issues.
- **CSS Reset**: add minimal reset — `body { margin: 0; padding: 0; }`, set body background to a neutral color (e.g., `#e8e5e0` or `#f0ede8`) so the mobile container pops against the desktop background when viewed on a larger screen.
- **Container shadow**: give the `.container` a subtle shadow on left and right (`box-shadow: 0 0 20px rgba(0,0,0,0.05)`) to simulate a phone screen when viewed on desktop. This is a nice touch for prototyping.
- **Flask graphic**: the pure CSS flask is the hero element of this page. Take care to position the bowl, neck, and rim correctly so it reads as a chemistry flask. Use `position: relative` on the 100×100 container and `position: absolute` on each part.
- **No images, no icon libraries**: everything is pure CSS or Unicode characters.
- **Mobile feel**: the page should feel like a native mobile app login screen — clean, minimal, focused. Keep spacing generous and avoid clutter.

---

## Visual Structure Summary

```
┌──────────────────────────────────────┐
│            (desktop bg)              │
│  ┌────────────────────────────┐      │
│  │       #faf8f5 bg           │      │
│  │                            │      │
│  │          ┌──┐              │      │
│  │          │  │ ← rim        │      │
│  │          │  │ ← neck       │      │
│  │          │  │              │      │
│  │         (    ) ← bowl      │      │
│  │          ~~~~  ← liquid    │      │
│  │                            │      │
│  │    ChemAI 智辅化学          │      │
│  │    你的AI化学学习伙伴        │      │
│  │                            │      │
│  │  ┌────────────────────┐    │      │
│  │  │ 请输入学号或手机号   │    │      │
│  │  └────────────────────┘    │      │
│  │  ┌────────────────────┐    │      │
│  │  │ 请输入密码      👁   │    │      │
│  │  └────────────────────┘    │      │
│  │                            │      │
│  │  ┌────────────────────┐    │      │
│  │  │       登录          │    │      │
│  │  └────────────────────┘    │      │
│  │                            │      │
│  │  还没有账号？联系老师注册    │      │
│  │          v0.1.0            │      │
│  │                            │      │
│  └────────────────────────────┘      │
│            (desktop bg)              │
└──────────────────────────────────────┘
       390px wide, 844px min-height
```
