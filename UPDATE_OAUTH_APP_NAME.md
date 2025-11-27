# How to Change OAuth App Name in Google Cloud Console

## Problem
The OAuth consent screen is showing "riva.ai" but you want it to show "riva.ai-2026"

## Solution

### Step 1: Go to OAuth Consent Screen
1. Open: https://console.cloud.google.com/apis/credentials/consent
2. Make sure you're in the correct project

### Step 2: Edit App Configuration
1. Click the **"EDIT APP"** button at the top of the page
2. This will take you to the "OAuth consent screen" tab

### Step 3: Change App Name
1. Find the **"App name"** field (should be near the top)
2. Change it from `riva.ai` to `riva.ai-2026`
3. Scroll down and click **"SAVE AND CONTINUE"**

### Step 4: Continue Through Tabs
You'll be taken through the configuration tabs:
1. **Scopes** - Click "SAVE AND CONTINUE" (no changes needed)
2. **Test users** - Click "SAVE AND CONTINUE" (no changes needed)
3. **Summary** - Click "BACK TO DASHBOARD"

### Step 5: Test Again
The change takes effect immediately. Run your test again:
```bash
python3 test_classroom.py
```

The OAuth consent screen should now show "riva.ai-2026" as the app name.

---

## Alternative: Which Project Are You Using?

It's possible you have two Google Cloud projects:
- One named "riva.ai" 
- One named "riva.ai-2026"

### Check Your Current Project
Look at the top of the Google Cloud Console page. You should see:
```
Google Cloud → [Project Name]
```

### If You're in the Wrong Project
1. Click the project dropdown
2. Select "riva.ai-2026" instead
3. Go through the OAuth consent screen setup for that project
4. Download new credentials.json from that project
5. Replace your current credentials.json

---

## Quick Fix: Just Update the App Name

If you just want to change the display name:
1. OAuth consent screen → EDIT APP
2. Change "App name" field
3. Save

That's it! The name shown during OAuth will update immediately.
