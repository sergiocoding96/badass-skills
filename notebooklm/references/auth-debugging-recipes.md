# Auth Debugging Recipes for notebooklm-py

## Problem: `notebooklm auth check` passes but `notebooklm list` fails

The `auth check` command only validates cookie file format — it does NOT verify cookie freshness with Google. You'll see:

```
Authentication Check
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check           ┃ Status    ┃ Details              ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Storage exists  │ ✓ pass    │ file                 │
│ JSON valid      │ ✓ pass    │                      │
│ Cookies present │ ✓ pass    │ 6 cookies            │
│ SID cookie      │ ✓ pass    │ .google.com          │
│ Token fetch     │ ⊘ skipped │ use --test to check  │
└─────────────────┴───────────┴──────────────────────┘
```

Yet `notebooklm list` returns:
```
Authentication expired or invalid. Redirected to: https://accounts.google.com/v3/signin/...
```

**Fix:** Run `notebooklm login --fresh` to get new cookies. Always verify with `notebooklm list`, not just `auth check`.

## Detecting Hermes Browser Engine

```bash
# Check which Playwright engine Hermes is using
ls /tmp/ | grep playwright_

# Chromium:  playwright_chromiumdev_profile-*
# Firefox:   playwright_firefoxdev_profile-*
```

## Reading Firefox Profile Cookies (Hermes Browser)

When Hermes uses Playwright Firefox, cookies ARE stored on disk:

```bash
# 1. Find the profile
PROFILE=$(ls -d /tmp/playwright_firefoxdev_profile-* | head -1)

# 2. Copy (DB is locked while Playwright runs)
cp "$PROFILE/cookies.sqlite" /tmp/firefox_cookies_copy.sqlite

# 3. Query Google auth cookies
sqlite3 /tmp/firefox_cookies_copy.sqlite \
  "SELECT name, value, host FROM moz_cookies WHERE host LIKE '%google%'"

# 4. Check for essential auth cookies
sqlite3 /tmp/firefox_cookies_copy.sqlite \
  "SELECT name, value FROM moz_cookies WHERE name IN
   ('SID', '__Secure-3PSID', 'HSID', 'SSID', 'APISID', 'SAPISID',
    '__Secure-1PSID', '__Secure-3PAPISID', '__Secure-1PAPISID', 'SIDCC')"
```

Expected result if NOT logged in: only NID, __Host-GAPS, OTZ, __Secure-ENID cookies.
Expected result if logged in: SID, HSID, APISID, SAPISID, etc.

## Reading Chromium Profile Cookies

```bash
PROFILE=$(ls -d /tmp/playwright_chromiumdev_profile-* | head -1)

# Chromium's Cookies SQLite might be empty (0 rows) if in-memory only
sqlite3 "$PROFILE/Default/Cookies" "SELECT COUNT(*) FROM cookies"
```

The Hermes Chromium profile has a `Default/Cookies` SQLite file but it's typically empty (just the schema, 0 rows). Cookies are in memory. To capture them, you need Playwright's `storage_state()` call.

## Detecting Stale vs Fresh Cookies

Cookies have an `expires_utc` field. Convert to human-readable:

```bash
# For Firefox
sqlite3 /tmp/firefox_cookies_copy.sqlite \
  "SELECT name, expires_utc, datetime(expires_utc/1000000 - 11644473600, 'unixepoch')
   FROM moz_cookies WHERE name='SID'"
```

Google SID cookies typically expire in ~6 months. Compare with current time to see if they're fresh or stale.

## Chrome Saved Passwords (encrypted, usually not accessible)

```bash
sqlite3 ~/.config/google-chrome/Default/'Login Data' \
  "SELECT origin_url, username_value FROM logins WHERE username_value LIKE '%gmail%'"
```

Passwords are stored in `password_value` as AES-256-CBC encrypted blobs. The key is in the GNOME keyring ("Chrome Safe Storage" entry), which is typically locked on headless servers. `secretstorage.get_default_collection()` returns a locked collection and `collection.unlock()` requires user interaction.

## gcloud OAuth Token (NOT usable for notebooklm-py)

```bash
# This works but can't authenticate notebooklm-py
gcloud auth print-access-token
```

The access token works for Google REST APIs (Drive, Gmail, Calendar, BigQuery) but notebooklm-py uses browser session cookies (SID/HSID/APISID/SAPISID), not OAuth. Direct API calls with `Authorization: Bearer <token>` to notebooklm.google.com return 405 or redirect to sign-in.
