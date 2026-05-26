# Chrome Cookie Encryption on Linux

## Problem

`notebooklm login --browser-cookies chrome` fails with:
- `Could not decrypt chrome cookies.`
- `rookiepy is not installed.` → after installing: `Could not decrypt chrome cookies.`
- `browser_cookie3.chrome()` → `BrowserCookieError: Unable to get key for cookie decryption`

## Root Cause

Chrome on Linux (v127+) stores cookies in SQLite with AES-256-CBC encryption. The decryption key is stored in the OS keyring (libsecret/gnome-keyring), NOT in the SQLite DB or Local State file.

### Key files

| File | Path | Purpose |
|------|------|---------|
| Cookie DB | `~/.config/google-chrome/Default/Cookies` | SQLite table: `cookies` with columns `name`, `value` (empty), `encrypted_value` (AES blob) |
| Login Data | `~/.config/google-chrome/Default/Login Data` | Saved passwords, same encryption |
| Local State | `~/.config/google-chrome/Local State` | Contains `os_crypt.encrypted_key` — but on modern systems this is empty (key is in OS keyring only) |

### Database evidence

```sql
SELECT host_key, name, length(encrypted_value)
FROM cookies 
WHERE host_key LIKE '%.google.com' AND name IN ('SID', 'HSID', 'APISID', 'SAPISID')
```

Results: all cookies show `value=''` (empty) and `encrypted_value` as 67-195 byte BLOBs. The `Local State` `os_crypt.encrypted_key` field is empty string on some distros — the key lives exclusively in libsecret.

### OS keyring access

On Ubuntu/Debian, the key is stored in GNOME Keyring accessible via D-Bus (org.freedesktop.secrets). Two Python libraries tried:

- **rookiepy** — fails because it can't access libsecret from D-Bus
- **browser-cookie3** — fails with `Unable to get key for cookie decryption`

`secret-tool` is also unavailable (not installed).

## Workarounds

1. **Local auth + copy**: Run `notebooklm login` on a Mac/Windows machine where the browser handles decryption, copy `storage_state.json` to server
2. **Hermes browser interactive**: Use the browser tool to navigate to notebooklm.google.com, enter credentials through Playwright
3. **Firefox** (if available): Firefox stores cookies unencrypted in a profile directory — `--browser-cookies firefox` would work

## Python code to inspect cookies (read-only, cannot decrypt)

```python
import sqlite3
conn = sqlite3.connect(f"file:~/.config/google-chrome/Default/Cookies?mode=ro", uri=True)
cur = conn.cursor()
cur.execute("SELECT host_key, name, length(encrypted_value) FROM cookies WHERE name IN ('SID','HSID')")
for r in cur.fetchall():
    print(f"{r[0]:30s} {r[1]:15s} encrypted={r[2]} bytes")
conn.close()
```
