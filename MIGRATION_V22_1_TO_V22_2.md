# USI17 V22.2 MIGRATION GUIDE

## Phase 1: Upload New Files to GitHub

### Step 1: Upload v22_2_translator.py
1. Go to your GitHub repo
2. Click "Add file" → "Upload files"
3. Upload `v22_2_translator.py`
4. Commit: "Add V22.2 translator (production-ready)"

### Step 2: Upload streamlit_app_v22_2_multi.py
1. Click "Add file" → "Upload files"
2. Upload `streamlit_app_v22_2_multi.py`
3. Commit: "Add V22.2 Streamlit app (production-ready)"

### Step 3: Verify Files
Check that you now have:
- ✅ v22_2_translator.py (NEW)
- ✅ streamlit_app_v22_2_multi.py (NEW)
- ⚠️ v22_1_translator.py (OLD - keep as backup)
- ⚠️ streamlit_app_v22_1_multi.py (OLD - keep as backup)

---

## Phase 2: Configure Streamlit

### Step 1: Go to Streamlit Dashboard
1. Visit https://share.streamlit.io
2. Find your USI17 app
3. Click the ⋮ menu → "Settings"

### Step 2: Update Main File
1. Look for "Main file path" or similar setting
2. Change from: `streamlit_app_v22_1_multi.py`
3. Change to: `streamlit_app_v22_2_multi.py`
4. Save changes

### Step 3: Reboot App
1. Click ⋮ menu → "Reboot app"
2. Wait ~30 seconds for restart
3. App will now use V22.2!

---

## Phase 3: Test V22.2

### Test 1: Initialization
1. Open your Streamlit app
2. Enter password (CKD2026USI17)
3. Enter API keys (Gemini, Grok)
4. Upload USI17_V22_2_MASTER.txt
5. Click "Initialize Translator"
6. Should see: "✅ V22.2 system loaded! 535 terms, 276 agents active"

### Test 2: Critical Term Fix
1. Source: Japanese
2. Target: English
3. Input: ショックキラー
4. Translate
5. Result should be: **"shock absorber"** ✅
6. NOT "Shock Killer" ❌

### Test 3: New Terms
1. Input: 体系表
2. Should translate to: "System Chart" ✅

1. Input: ストレート取付
2. Should translate to: "Inline Mount" ✅

### Test 4: Multi-Language
1. Source: Japanese
2. Targets: Select English, German, French
3. Input: ショックキラー
4. All 3 should show "shock absorber" variations ✅

---

## Phase 4: Cleanup (After Successful Testing)

### ONLY do this AFTER V22.2 works perfectly!

### Optional: Delete Old V22.1 Files
1. Go to GitHub repo
2. Click `v22_1_translator.py`
3. Click trash icon → Delete
4. Commit: "Remove V22.1 (replaced by V22.2)"

5. Click `streamlit_app_v22_1_multi.py`
6. Delete
7. Commit: "Remove V22.1 app (replaced by V22.2)"

### Recommended: Keep as Backup
- Just leave the V22.1 files there
- They won't interfere with V22.2
- Can rollback if needed

---

## Verification Checklist

Before declaring success, verify:

- [  ] ✅ V22.2 files uploaded to GitHub
- [  ] ✅ Streamlit configured for V22.2
- [  ] ✅ App initializes successfully
- [  ] ✅ ショックキラー → "shock absorber" ✅
- [  ] ✅ New terms work (体系表, etc.)
- [  ] ✅ Multi-language translation works
- [  ] ✅ Cost tracking works
- [  ] ✅ Translation Memory works
- [  ] ✅ No errors in console

---

## Rollback Procedure (If Needed)

If V22.2 has problems:

1. Go to Streamlit dashboard
2. Settings → Main file path
3. Change back to: `streamlit_app_v22_1_multi.py`
4. Reboot app
5. You're back on V22.1

---

## Support

Issues? Contact:
- Email: chris248ma@gmail.com
- Check GitHub commits for recent changes
- Review error messages in Streamlit console

---

## Success Criteria

V22.2 is production-ready when:
1. ✅ All tests pass
2. ✅ No `simplification_result` errors
3. ✅ Glossary terms correct (535 terms)
4. ✅ Performance same or better than V22.1
5. ✅ You're confident using it for production work

---

END OF MIGRATION GUIDE