# Hermes Browser In-Memory Cookie Architecture

## Discovery (May 2026)

The Hermes browser tool uses Playwright with a Chromium browser that runs from a Cloak installation at `/home/openclaw/.cloakbrowser/chromium-146.0.7680.177.4/chrome`. This is NOT the system Chrome at `/usr/bin/google-chrome-stable`.

## Temp Profile Structure

When the Hermes browser tool is used (browser_navigate etc.), Playwright creates a temp user data directory:

```
/tmp/playwright_chromiumdev_profile-<random_suffix>/
├── Default/
│   ├── Cache/
│   ├── Local Storage/
│   ├── History              (SQLite)
│   ├── Login Data           (SQLite, encrypted passwords)
│   ├── Preferences
│   └── ... (NO Cookies file!)
├── Local State              (empty os_crypt.encrypted_key)
├── SingletonCookie → <inode_number>  (symlink to shared memory)
└── ...
```

Key observations:
- No `Default/Cookies` SQLite database exists — cookies are held in Chromium's process memory only
- The `SingletonCookie` is a symlink to a Linux inode/SHIM handle, not a file
- `document.cookie` in JS returns only non-HttpOnly cookies (SID, APISID, SAPISID) — critical auth cookies like `__Secure-3PSID`, `HSID`, `SSID` are HttpOnly and invisible to JS
- The Cloak Chromium process runs continuously (started May 24 in our case): `ps aux | grep cloakbrowser` shows the main chrome process and zygote children

## Why Cookie Extraction Fails

| Method | Result | Reason |
|--------|--------|--------|
| `rookiepy.chrome()` | "no Google cookies" | Looks at system Chrome, not Playwright profile |
| `browser-cookie3.chrome()` | `Unable to get key for decryption` | System Chrome cookies encrypted with AES-256-CBC, key in libsecret |
| SQLite on `Cookies` file | File doesn't exist | No Cookies DB in temp profile |
| `document.cookie` | Only 6 non-HttpOnly cookies | Missing `__Secure-3PSID`, `HSID`, `SSID` |
| Playwright `storage_state()` | Works — but only from within the Playwright context | Need access to the same user_data_dir |

## How to Extract

1. Find the temp profile path from process list: `ps aux | grep playwright | grep --user-data-dir`
2. Use Playwright Python API with `launch_persistent_context(user_data_dir=<that_path>)`
3. Navigate to NotebookLM and call `context.storage_state()`
4. Save to `~/.notebooklm/profiles/default/storage_state.json`

## Verification

```python
from playwright.sync_api import sync_playwright
ctx = p.chromium.launch_persistent_context(user_data_dir=TEMP_PROFILE, headless=True)
storage = ctx.storage_state()
# Check for SID cookie
sid = [c for c in storage["cookies"] if c["name"] == "SID"]
print(f"SID present: {len(sid) > 0}")
```
