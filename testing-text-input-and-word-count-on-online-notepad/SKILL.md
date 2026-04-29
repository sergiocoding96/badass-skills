---
name: testing-text-input-and-word-count-on-online-notepad
description: "Testing Text Input and Word Count on Online Notepad in Google Chrome. Generated from live Screenpipe capture."
version: 2.0.0
read_when:
  - "Testing Text Input and Word Count on Online Notepad"
  - "Google Chrome workflow"
  - "Browser testing workflow"
metadata: {"hermes":{"emoji":"🎬"}}
allowed-tools: browser(*)
---

# Testing Text Input and Word Count on Online Notepad

- **Application**: Browser (Hermes MCP)
- **URL Pattern**: `onlinenotepad.org/notepad`
- **Login Required**: No

## Summary

The user transfers text from a local Notepad application to an online notepad tool, dismisses an interstitial ad, and then tests the online editor's word count and autosave features by clearing the page and manually typing 'test' on multiple lines.

## Setup

```
mcp_browser_navigate(url="https://onlinenotepad.org/notepad")
mcp_browser_snapshot(full=false)  # Get interactive elements
```

## Steps

### 1. NAVIGATE: onlinenotepad.org/notepad

> *Navigate to the Online Notepad website.*

**Why**: To use the web-based text editor for note taking or testing.

**Execute**:
```
mcp_browser_navigate(url="https://onlinenotepad.org/notepad")
mcp_browser_snapshot(full=false)  # Refresh refs
```

**Verify**: The Online Notepad website loads, potentially showing a consent dialog.

**Visual Reference**: `references/frames/step_1.jpg`

**If it fails**: Page fails to load or a consent dialog blocks interaction.

---

### 2. ACCEPT CONSENT (if dialog appears)

> *Dismiss the consent dialog to access the notepad interface.*

**Why**: The consent dialog prevents interaction with the main web application.

**Execute**:
```
# Look for any accept/agree button in the snapshot
# If dialog present, click the primary action button (e.g. "Accept" or "Agree")
# If no explicit button, try pressing Enter to accept defaults
mcp_browser_press(key="Enter")
mcp_browser_snapshot(full=false)  # Refresh after dismiss attempt
```

**Verify**: The dialog disappears, revealing the notepad editor.

**If it fails**: Try clicking directly in the main content area, or navigate again.

---

### 3. KEYBOARD_SHORTCUT: Control+V

> *Paste the text copied from the local Notepad application.*

**Why**: To transfer draft content to the online tool for editing or storage.

**Execute**:
```
mcp_browser_press(key="Control+V")
mcp_browser_snapshot(full=false)  # Check result
```

**Verify**: Multiple lines containing the word 'test' appear in the editor, and the word count updates.

**If it fails**: Clipboard is empty or paste fails due to browser permissions. Try manually typing instead.

---

### 4. KEYBOARD_SHORTCUT: Control+A

> *Select all text in the editor.*

**Why**: Preparing to clear the editor to start a new test.

**Execute**:
```
mcp_browser_press(key="Control+A")
```

**Verify**: All text in the document is highlighted.

**If it fails**: Focus is not on the text editor. Click on the editor area first.

---

### 5. KEYBOARD_SHORTCUT: Backspace

> *Delete the selected text.*

**Why**: To empty the notepad for fresh input.

**Execute**:
```
mcp_browser_press(key="Backspace")
mcp_browser_snapshot(full=false)  # Verify word count resets
```

**Verify**: The editor is empty and the word count resets to 0.

**If it fails**: Try clicking in editor first to ensure focus.

---

### 6. TYPE: test

> *Type the word 'test' in the editor.*

**Why**: To test the real-time word counter and autosave functionality.

**Execute**:
```
# First locate the textbox in the snapshot - look for iframe or textbox element
# Click on it to focus, then type
mcp_browser_click(ref="@e{N}")  # Use the ref from snapshot for the editor/textbox
mcp_browser_type(ref="@e{N}", text="test")
```

**Alternative** (if textbox not clearly identifiable):
```
# Use keyboard to type directly if editor area is focused
mcp_browser_type(ref="@e{N}", text="test")
```

**Verify**: The word appears in the document and the word count updates.

**Visual Reference**: `references/frames/step_6.jpg`

**If it fails**: Try pressing Tab to focus the editor, then type directly.

---

## Decision Points

- **Step 2**: Consent dialog handling → If a consent dialog appears, try pressing Enter first (accepts defaults). If that doesn't work, look for an "Accept" or "Agree" button in the snapshot and click it.
- **Step 6**: If the textbox ref is not identifiable in the snapshot, try clicking on the main content area (often inside an iframe) to focus it before typing.

## Hermes Browser Tool Reference

| OpenClaw Command | Hermes MCP Tool |
|------------------|-----------------|
| `openclaw browser open` | `mcp_browser_navigate` |
| `openclaw browser snapshot --interactive` | `mcp_browser_snapshot(full=false)` |
| `openclaw browser find role button --name "X" click` | `mcp_browser_click(ref="@eN")` — find button ref in snapshot |
| `openclaw browser key "Control+V"` | `mcp_browser_press(key="Control+V")` |
| `openclaw browser find role textbox --name "X" fill "text"` | `mcp_browser_click` to focus + `mcp_browser_type` to enter text |

## Agent Tips

1. Always `mcp_browser_snapshot(full=false)` after navigation to get fresh refs
2. Refs change on every page load — never reuse refs from a previous session
3. If the consent dialog blocks interaction, press Enter first to dismiss it
4. Verify each step using the **Verify** notes before proceeding
5. The editor is often inside an iframe — click on the iframe area to focus it

---
*Adapted from OpenClaw Screenpipe capture for Hermes MCP browser tools*