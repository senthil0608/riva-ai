# How to Find OAuth Consent Screen in Google Cloud Console

## Step-by-Step Navigation

### 1. Go to Google Cloud Console
Open: https://console.cloud.google.com/

### 2. Select Your Project
- At the top of the page, click the **project dropdown** (next to "Google Cloud")
- Select the project where you created your credentials
- If you don't have a project, create one first

### 3. Navigate to OAuth Consent Screen

**Option A: Using the Search Bar (Fastest)**
1. Click the search bar at the top
2. Type: **"OAuth consent screen"**
3. Click on **"OAuth consent screen"** in the results

**Option B: Using the Menu**
1. Click the **hamburger menu** (☰) in the top-left corner
2. Scroll down to **"APIs & Services"**
3. Hover over it to expand the submenu
4. Click **"OAuth consent screen"**

### 4. What You Should See

Once you're on the OAuth consent screen page, you should see:

#### At the Top:
- **User Type** section with radio buttons:
  - ⚪ Internal (Only for Google Workspace)
  - ⚪ External (For anyone with a Google account)

#### Tabs Below:
1. **OAuth consent screen** (main configuration)
2. **Scopes** (API permissions)
3. **Test users** (who can use your app in testing mode)
4. **Summary**

---

## If You Don't See These Options

### Scenario 1: You See "Configure Consent Screen" Button
This means the OAuth consent screen hasn't been set up yet.

**Action:**
1. Click **"CONFIGURE CONSENT SCREEN"**
2. Choose **"External"** as User Type
3. Click **"CREATE"**

### Scenario 2: You're on a Different Page
You might be on the "Credentials" page instead.

**Action:**
1. Look at the left sidebar
2. Click **"OAuth consent screen"** (should be above "Credentials")

### Scenario 3: OAuth Consent Screen is Already Configured
If you already configured it, you won't see the User Type selection again.

**To check/edit:**
1. You should see **"EDIT APP"** button at the top
2. Click it to modify settings
3. The User Type is shown but not editable (you'd need to delete and recreate to change it)

---

## Configuring OAuth Consent Screen (First Time)

### Step 1: User Type
- Select **"External"**
- Click **"CREATE"**

### Step 2: OAuth Consent Screen Tab

Fill in required fields:
- **App name:** `Riva AI Classroom` (or any name)
- **User support email:** Select your email from dropdown
- **Developer contact information:** Enter your email

Optional fields (can skip):
- App logo
- App domain
- Authorized domains

Click **"SAVE AND CONTINUE"**

### Step 3: Scopes Tab

1. Click **"ADD OR REMOVE SCOPES"**
2. In the filter box, search for: **"classroom"**
3. Check these three scopes:
   - ✅ `https://www.googleapis.com/auth/classroom.courses.readonly`
   - ✅ `https://www.googleapis.com/auth/classroom.coursework.students.readonly`
   - ✅ `https://www.googleapis.com/auth/classroom.rosters.readonly`
4. Click **"UPDATE"**
5. Click **"SAVE AND CONTINUE"**

### Step 4: Test Users Tab

> [!IMPORTANT]
> This is the CRITICAL step that fixes the "Access blocked" error!

1. Click **"ADD USERS"**
2. Enter the Gmail address you'll use for testing
3. Click **"ADD"**
4. Click **"SAVE AND CONTINUE"**

### Step 5: Summary Tab
- Review your settings
- Click **"BACK TO DASHBOARD"**

---

## If You Still Can't Find It

### Check Your Project
Make sure you're in the correct project:
- Look at the top bar: **"Google Cloud" → [Your Project Name]**
- If it says "Select a project", you need to select or create one first

### Create a Project First
If you don't have a project:

1. Click the project dropdown at the top
2. Click **"NEW PROJECT"**
3. Enter a name: `Riva AI`
4. Click **"CREATE"**
5. Wait for it to be created (takes a few seconds)
6. Then navigate to OAuth consent screen

### Enable Google Classroom API First
Sometimes the OAuth consent screen requires an API to be enabled first:

1. Go to **APIs & Services → Library**
2. Search for **"Google Classroom API"**
3. Click on it
4. Click **"ENABLE"**
5. Then go back to OAuth consent screen

---

## Quick Visual Reference

```
Google Cloud Console
├── [Project Selector] ← Make sure a project is selected
├── ☰ Menu
    └── APIs & Services
        ├── OAuth consent screen ← YOU WANT THIS
        │   ├── User Type (External/Internal)
        │   ├── OAuth consent screen tab
        │   ├── Scopes tab ← Add Classroom scopes here
        │   ├── Test users tab ← Add your email here
        │   └── Summary tab
        ├── Credentials ← Different page (for client ID)
        └── Library ← Enable APIs here
```

---

## After Configuration

Once you've configured the OAuth consent screen:

1. Go to **"Credentials"** (in the left sidebar)
2. Create or verify your OAuth 2.0 Client ID
3. Download `credentials.json`
4. Delete old `token.pickle` if it exists
5. Run your test script

---

## Still Having Issues?

If you're still not seeing the OAuth consent screen options, please check:

1. **Are you logged in with the correct Google account?**
   - The account must have Owner or Editor permissions on the project

2. **Is billing enabled?** (Usually not required for OAuth, but sometimes needed)
   - Go to **Billing** in the menu
   - Link a billing account if prompted

3. **Try a different browser or incognito mode**
   - Sometimes browser extensions interfere

4. **Direct link to OAuth consent screen:**
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```
   - Replace the URL with your project ID:
   ```
   https://console.cloud.google.com/apis/credentials/consent?project=YOUR_PROJECT_ID
   ```

Let me know what you see and I can help further!
