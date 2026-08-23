# Google Stitch Prompt: Parent Login Page (m/parent-login.html)

---

Generate a single, self-contained HTML file (`m/parent-login.html`) for a parent mobile login page. Use **vanilla HTML + CSS only** — no frameworks, no libraries. All CSS and HTML in one file. This is a static prototype with no JavaScript interaction needed (optional: simple input focus styling, binding code numeric-only validation hint).

---

## Global Design Tokens

- **Primary color**: Oxford Blue `#002045`
- **Accent / Teal**: `#13696a`
- **Background**: warm paper `#faf8f5`
- **Info card background**: light blue `#e3f2fd`
- **Font stack**: Headings — `'Cormorant Garamond', serif`; Body — `'IBM Plex Sans', sans-serif` (load from Google Fonts)
- **Border radius**: Inputs `8px`, Buttons `8px`, Info card `8px`, Parent tag `9999px` (pill)
- **Target viewport**: Mobile — `max-width: 390px`, `min-height: 844px`, centered with `margin: 0 auto`
- **Body background**: `#e8e5e0` (desktop backdrop)

---

## Page Container

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

Centers all content vertically and horizontally. The outer body background is `#e8e5e0` so the phone container stands out on desktop. Add `box-shadow: 0 0 20px rgba(0,0,0,0.05)` to the container.

---

## Component 1 — Logo Area

A centered flexbox column, `text-align: center`, `margin-bottom: 32px`:

### App Title Row
`display: flex`, `align-items: center`, `justify-content: center`, `gap: 8px`:

- **"ChemAI 智辅化学"**: Oxford Blue `#002045`, `22px`, bold, Cormorant Garamond
- **"家长端" (Parent Version) tag**: inline pill, Teal `#13696a` background, white text, `12px`, `font-weight: 500`, `border-radius: 9999px`, `padding: 2px 10px`, IBM Plex Sans. This tag sits to the right of the title.

### Description Text
`margin-top: 12px`, `font-size: 14px`, `color: #888`, IBM Plex Sans, `text-align: center`, `max-width: 280px`, `line-height: 1.5`:
- "使用手机号和绑定码登录，查看孩子的学习情况" (Log in with your phone number and binding code to view your child's learning progress)

---

## Component 2 — Login Form

A form container with `width: 320px`, `margin: 0 auto`. Use a plain `<div>` (no actual `<form>` submission needed).

### Phone Number Input

A wrapper `<div>` with `position: relative`:

- **Phone icon** (left side, inside the input area):
  - Unicode character `📱` or a simple CSS phone shape positioned absolutely: `left: 14px`, `top: 50%`, `transform: translateY(-50%)`, `font-size: 16px`, `color: #aaa`, `pointer-events: none`, `z-index: 1`
- **Input**:
  - `<input type="tel">`, `width: 100%`, `height: 48px`
  - `border-radius: 8px`, `border: 1px solid #ddd`
  - `padding: 0 14px 0 40px` (left padding to make room for the phone icon)
  - `font-size: 15px`, IBM Plex Sans, `color: #333`
  - `background: white`, `box-sizing: border-box`
  - Placeholder: `"请输入手机号"` (Please enter phone number)
  - `inputmode: numeric` (hints mobile keyboard to show number pad)
- **Focus state**: `border-color: #002045`, `box-shadow: 0 0 0 3px rgba(0,32,69,0.1)`, `outline: none`
- `margin-bottom: 12px`

### Binding Code Input

Same wrapper pattern:

- **Lock or key icon** (left side): Unicode `🔑` or `#` or a simple CSS lock shape, `left: 14px`, `top: 50%`, `transform: translateY(-50%)`, `font-size: 15px`, `color: #aaa`, `pointer-events: none`, `z-index: 1`
- **Input**:
  - `<input type="text">`, `width: 100%`, `height: 48px`
  - `border-radius: 8px`, `border: 1px solid #ddd`
  - `padding: 0 14px 0 40px`
  - `font-size: 15px`, IBM Plex Sans, `color: #333`
  - `background: white`, `box-sizing: border-box`
  - `maxlength: 6` (limit to 6 characters)
  - `inputmode: numeric` (numeric keyboard on mobile)
  - `letter-spacing: 4px` (spread out the 6 digits for readability, like a verification code)
  - `text-align: left` (but the letter-spacing gives it a code-like feel)
  - Placeholder: `"请输入6位绑定码"` (Please enter 6-digit binding code)
- **Focus state**: same as phone input — `border-color: #002045`, `box-shadow: 0 0 0 3px rgba(0,32,69,0.1)`, `outline: none`

### Binding Code Hint Text
`font-size: 12px`, `color: #aaa`, IBM Plex Sans, `margin-top: 4px`, `padding-left: 2px`:
- "绑定码可在孩子App的'我的'页面找到" (The binding code can be found on your child's 'My Profile' page in the app)

### Login Button
- Full-width button: `width: 320px`, `height: 48px`
- Oxford Blue `#002045` background, white text
- `font-size: 16px`, `font-weight: 500`, IBM Plex Sans
- `border-radius: 8px`, `border: none`, `cursor: pointer`
- `margin-top: 24px`
- Text: "登录" (Login)
- **Hover state**: `background: #1a365d`
- **Active/press state**: `background: #001a35`, `transform: scale(0.98)`
- `transition: background 0.2s, transform 0.1s`

---

## Component 3 — Binding Code Info Card

A light blue info card, `width: 320px`, `margin: 20px auto 0`, `background: #e3f2fd`, `border-radius: 8px`, `padding: 14px 16px`:

- **Bold title**: "什么是绑定码？" (What is a binding code?), `14px`, `font-weight: 600`, color `#1a5276` (dark blue), IBM Plex Sans
- **Description text**: `13px`, `color: #555`, IBM Plex Sans, `margin-top: 4px`, `line-height: 1.5`:
  - "绑定码是6位数字，用于关联您和孩子的账号。请让孩子在他的ChemAI App中查看。" (The binding code is a 6-digit number used to link your account with your child's. Please ask your child to check it in their ChemAI app.)
- Optional: a small info icon `ℹ️` or `💡` at the top-left of the card (or inline before the title) to make it look helpful and friendly.

---

## Component 4 — Footer Text

Centered below the form and info card, `margin-top: 32px`, `text-align: center`:

### Help Link
- Text: "如何获取绑定码？" (How to get the binding code?)
- `font-size: 14px`, IBM Plex Sans
- Color: Teal `#13696a`, `text-decoration: underline`, `cursor: pointer`
- Hover: color darkens slightly

### Version Number
- Text: "v0.1.0"
- `font-size: 12px`, IBM Plex Sans
- Color: light gray `#bbb`
- `margin-top: 12px`

---

## CSS / Implementation Notes

- **Single file output**: all HTML and CSS in one file. No JavaScript needed for this static prototype.
- **Google Fonts**: load Cormorant Garamond (400, 700) and IBM Plex Sans (400, 500) via a `<link>` in `<head>`.
- **Box sizing**: use `* { box-sizing: border-box; }` globally.
- **CSS Reset**: `body { margin: 0; padding: 0; background: #e8e5e0; }`.
- **Container shadow**: `box-shadow: 0 0 20px rgba(0,0,0,0.05)` to simulate a phone screen on desktop.
- **Icons**: use Unicode characters (📱 phone, 🔑 key, ℹ️ info, 💡 tip). No icon libraries.
- **No images**: everything is pure CSS or Unicode.
- **Binding code input**: the `letter-spacing: 4px` is important — it makes the 6-digit code look like a verification code, giving it a distinctive visual treatment. Combined with `maxlength: 6` and `inputmode: numeric`, the input feels purpose-built for a short code.
- **Parent tag**: the Teal `#13696a` pill next to "ChemAI 智辅化学" visually distinguishes this as the parent version from the student version. This is a key branding differentiator.
- **Info card**: the light blue `#e3f2fd` background makes the help information stand out without being aggressive. It should feel like a friendly tooltip.
- **Input icons**: the phone 📱 and key 🔑 icons inside the inputs help users quickly identify what each field is for, reducing cognitive load.
- **Mobile feel**: the page should feel warm, trustworthy, and simple — parents may not be tech-savvy, so clarity and reassurance are paramount.

---

## Visual Structure Summary

```
┌──────────────────────────────────────┐
│            (desktop bg)              │
│  ┌────────────────────────────┐      │
│  │       #faf8f5 bg           │      │
│  │                            │      │
│  │  ChemAI 智辅化学 [家长端]   │      │ ← Logo + parent tag
│  │  使用手机号和绑定码登录，    │      │ ← Description
│  │  查看孩子的学习情况          │      │
│  │                            │      │
│  │  ┌──────────────────────┐  │      │
│  │  │ 📱 请输入手机号        │  │      │ ← Phone input (icon left)
│  │  └──────────────────────┘  │      │
│  │                            │      │
│  │  ┌──────────────────────┐  │      │
│  │  │ 🔑 请输入6位绑定码     │  │      │ ← Binding code input
│  │  └──────────────────────┘  │      │   (letter-spacing, maxlength 6)
│  │  绑定码可在孩子App的       │      │ ← Hint text
│  │  '我的'页面找到            │      │
│  │                            │      │
│  │  ┌──────────────────────┐  │      │
│  │  │        登录           │  │      │ ← Oxford Blue button
│  │  └──────────────────────┘  │      │
│  │                            │      │
│  │  ┌──────────────────────┐  │      │
│  │  │ 💡 什么是绑定码？     │  │      │ ← Info card (light blue)
│  │  │ 绑定码是6位数字...    │  │      │
│  │  └──────────────────────┘  │      │
│  │                            │      │
│  │     如何获取绑定码？        │      │ ← Teal link
│  │          v0.1.0            │      │ ← Version
│  │                            │      │
│  └────────────────────────────┘      │
│            (desktop bg)              │
└──────────────────────────────────────┘
       390px wide, 844px min-height
```

---

## Key Differences from Student Login

This parent login page is intentionally simpler and more guided than the student login:

| Aspect | Student Login | Parent Login |
|--------|--------------|--------------|
| Auth method | Student ID + Password | Phone number + Binding code |
| Visual identity | Chemistry flask graphic | "家长端" Teal pill tag |
| Input count | 2 (ID + password) | 2 (phone + 6-digit code) |
| Password toggle | Yes (eye icon) | No (binding code, not password) |
| Help section | None | Light blue info card explaining binding code |
| Input style | Standard | Code input with letter-spacing |
| Tone | Student-focused, academic | Parent-focused, reassuring |

These differences reflect the distinct needs of each user: students log in with familiar credentials, while parents need guidance on the binding code concept.
