# Google Classroom OAuth Fix Guide

## Problem
You're seeing: **"Access blocked: This app's request is invalid"**

This error occurs during Google OAuth authentication and is typically caused by OAuth consent screen misconfiguration.

---

## Root Causes

The error happens when one or more of these conditions exist:

1. **OAuth consent screen not properly configured**
2. **App is in "Testing" mode but user isn't added as test user**
3. **Invalid redirect URI configuration**
4. **Missing required OAuth scopes**
5. **Incorrect application type selected**

---

## Solution Steps

### Step 1: Verify OAuth Consent Screen

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **OAuth consent screen**

#### Check These Settings:

**User Type:**
- If you see "Internal" - only works for Google Workspace accounts
- **Recommended:** Select **"External"** for personal Gmail accounts

**App Information:**
- App name: Enter any name (e.g., "Riva AI Classroom")
- User support email: Your email
- Developer contact: Your email

**Scopes:**
Ensure these scopes are added:
```
https://www.googleapis.com/auth/classroom.courses.readonly
https://www.googleapis.com/auth/classroom.coursework.students.readonly
https://www.googleapis.com/auth/classroom.rosters.readonly
```

**Test Users (CRITICAL if app is in Testing mode):**
- Click **"ADD USERS"**
- Add the Gmail account you're testing with
- **This is the most common cause of the error!**

### Step 2: Verify OAuth Client Configuration

1. Go to **APIs & Services** → **Credentials**
2. Find your OAuth 2.0 Client ID
3. Click the edit icon (pencil)

#### Verify Settings:

**Application type:** Must be **"Desktop app"**

**Authorized redirect URIs:**
For desktop apps, this should typically be:
```
http://localhost
```

> [!IMPORTANT]
> If you created a "Web application" instead of "Desktop app", you need to:
> 1. Delete the existing OAuth client
> 2. Create a new one with type "Desktop app"
> 3. Download the new credentials.json

### Step 3: Update credentials.json

1. After making changes, download fresh credentials:
   - Click the download icon next to your OAuth client
   - Save as `credentials.json` in your project root
   - Replace the old file

2. **Delete the old token:**
   ```bash
   rm token.pickle
   ```
   This forces re-authentication with the new settings.

### Step 4: Re-authenticate

Run your test script again:
```bash
python test_classroom.py
```

The OAuth flow should now work correctly.

---

## Quick Checklist

Before running the test again, verify:

- [ ] OAuth consent screen user type is "External" (unless using Workspace)
- [ ] Your test email is added to "Test users" list
- [ ] OAuth client type is "Desktop app" (not "Web application")
- [ ] All three Classroom API scopes are added
- [ ] Fresh credentials.json downloaded
- [ ] Old token.pickle deleted

---

## Common Mistakes

### ❌ Wrong Application Type
**Problem:** Created "Web application" instead of "Desktop app"
**Fix:** Delete and recreate as Desktop app

### ❌ Not Added as Test User
**Problem:** App in Testing mode, but user not in test users list
**Fix:** Add your email to test users in OAuth consent screen

### ❌ Internal User Type with Gmail
**Problem:** Selected "Internal" but using personal Gmail
**Fix:** Change to "External" user type

### ❌ Cached Credentials
**Problem:** Old token.pickle has invalid credentials
**Fix:** Delete token.pickle and re-authenticate

---

## Verification

After fixing, you should see:

1. Browser opens to Google sign-in
2. Account selection screen
3. Permission request screen showing:
   - "See your Google Classroom classes"
   - "View your course work and grades"
   - "View your Google Classroom class rosters"
4. Success message in terminal

---

## Still Having Issues?

### Check Application Status

In Google Cloud Console → OAuth consent screen:

**Publishing status:**
- "Testing" = Only test users can access (most restrictive)
- "In production" = Anyone can access (requires verification for sensitive scopes)

For development, "Testing" mode is fine, but **you must add test users**.

### Enable Required APIs

Ensure Google Classroom API is enabled:
1. Go to **APIs & Services** → **Library**
2. Search for "Google Classroom API"
3. Click **ENABLE** if not already enabled

### Check Credentials File Format

Your `credentials.json` should look like this:
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

Note the **"installed"** key - this indicates Desktop app type.

If you see **"web"** instead, you have the wrong type!

---

## Next Steps

Once OAuth is working:

1. Run the full test suite:
   ```bash
   python test_classroom.py
   ```

2. If successful, you'll see:
   - ✅ Authentication
   - ✅ List Courses
   - ✅ List Assignments
   - ✅ classroom_sync_agent

3. The `token.pickle` file will be created and reused for future requests

---

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Classroom API Quickstart](https://developers.google.com/classroom/quickstart/python)
- [OAuth Consent Screen Setup](https://support.google.com/cloud/answer/10311615)
