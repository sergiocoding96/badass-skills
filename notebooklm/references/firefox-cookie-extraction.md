# Firefox Cookie → Playwright storage_state.json Conversion

After successfully signing into notebooklm.google.com through the Hermes browser (when using the Firefox Playwright engine), cookies live in a SQLite database on disk. This reference shows how to extract them and save as a `storage_state.json` that `notebooklm-py` CLI can use.

## Prerequisites

The Hermes browser session must still be alive (cookies.sqlite file must exist and be accessible). If the session was interrupted, the profile is cleaned up and you'll need to re-auth.

## Step-by-step

### 1. Find the Firefox profile

```bash
ls /tmp/ | grep playwright_firefox
# → playwright_firefoxdev_profile-r3mwN2
PROFILE=$(ls -d /tmp/playwright_firefoxdev_profile-* 2>/dev/null | head -1)
```

If nothing is found but a Chromium profile is present, cookies are in-memory (see `hermes-browser-in-memory-cookies.md`).

### 2. Copy the cookies database (it's locked by Playwright)

```bash
cp "$PROFILE/cookies.sqlite" /tmp/firefox_cookies_copy.sqlite
```

### 3. Verify auth cookies exist

```bash
sqlite3 /tmp/firefox_cookies_copy.sqlite \
  "SELECT name, value FROM moz_cookies WHERE name IN
   ('SID', '__Secure-3PSID', 'HSID', 'SSID', 'APISID', 'SAPISID',
    '__Secure-1PSID', '__Secure-3PAPISID', '__Secure-1PAPISID', 'SIDCC')"
```

If only pre-session cookies appear (NID, __Host-GAPS, OTZ, __Secure-ENID), the user never completed Google sign-in in the Hermes browser. Go back and sign in first.

### 4. Convert to Playwright storage_state.json

Run this Python script:

```python
import sqlite3, json
from pathlib import Path

cookies_path = "/tmp/firefox_cookies_copy.sqlite"
storage_path = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"

conn = sqlite3.connect(cookies_path)
cursor = conn.cursor()

# Get all relevant Google auth cookies, deduplicated by (name, domain)
cursor.execute("""
    SELECT DISTINCT name, value, host, path, isSecure, isHttpOnly, expiry 
    FROM moz_cookies 
    WHERE host LIKE '%.google.com' 
       OR host LIKE '%notebooklm.google.com' 
       OR host LIKE '%accounts.google.com'
    ORDER BY name
""")
rows = cursor.fetchall()
conn.close()

playwright_cookies = []
for r in rows:
    name, value, host, path, is_secure, is_httponly, expiry = r
    # Skip expired cookies
    if expiry and expiry < 1700000000:
        continue
    playwright_cookies.append({
        "name": name,
        "value": value,
        "domain": host,
        "path": path,
        "httpOnly": bool(is_httponly),
        "secure": bool(is_secure),
        "sameSite": "None",
        "expires": expiry if expiry else 1779858605
    })

storage_path.parent.mkdir(parents=True, exist_ok=True)
with open(storage_path, "w") as f:
    json.dump({"cookies": playwright_cookies, "origins": []}, f, indent=2)

print(f"Saved {len(playwright_cookies)} cookies to {storage_path}")
```

### 5. Verify

```bash
notebooklm auth check --test
# All checks should pass, including Token fetch
notebooklm list
# Should list notebooks without redirect error
```

## Common Pitfalls

### "Database is locked" error
The original `cookies.sqlite` is locked by the running Playwright process. Always copy it first — never query the original DB directly.

### Only 4 cookies after sign-in
If the Hermes browser was used to navigate to accounts.google.com but the sign-in flow was not completed (user entered email but didn't go through password page), only pre-session cookies exist. You need to complete the full Google sign-in through the Hermes browser.

### Some rows have domain .google.es or other regional domains
Firefox stores separate cookies per domain TLD. Deduplicate by name+domain and keep only `.google.com` for the storage_state.json. The notebooklm-py client only needs cookies from `.google.com`, `notebooklm.google.com`, and `accounts.google.com`.

### Storage path doesn't exist
The `~/.notebooklm/profiles/default/` directory might not exist yet if `notebooklm login` was never run. Create it: `mkdir -p ~/.notebooklm/profiles/default/`
