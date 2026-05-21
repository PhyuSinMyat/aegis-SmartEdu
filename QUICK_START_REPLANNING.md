# Quick Start: Verify Replanning System

## ⚡ 30-Second Check

```bash
# Run the diagnostic tool
python diagnose_replanning.py
```

**Expected Result:**
```
╔══════════════════════════════════════════════════════════╗
║  REPLANNING SYSTEM DIAGNOSTIC TOOL                       ║
╚══════════════════════════════════════════════════════════╝

...checks...

═══════════════════════════════════════════════════════════
 DIAGNOSTIC SUMMARY
═══════════════════════════════════════════════════════════
  PASS                 Imports
  PASS                 Config
  PASS                 Database
  PASS                 Files
  PASS                 Frontend
  PASS                 Backend
  PASS                 Functional

────────────────────────────────────────────────────────────
  Result: 7/7 checks passed
────────────────────────────────────────────────────────────

🎉 SUCCESS: Replanning system is properly configured!
```

✅ **If all 7 checks pass** → System is working!  
❌ **If any check fails** → See troubleshooting below

---

## 🧪 2-Minute Full Test

```bash
# Run comprehensive test suite
python test_replanning_comprehensive.py
```

**Expected Result:**
```
████████████████████████████████████████████████████████████████████
█  COMPREHENSIVE REPLANNING SYSTEM TEST
████████████████████████████████████████████████████████████████████

[... 6 tests run ...]

═══════════════════════════════════════════════════════════
 TEST SUMMARY
═══════════════════════════════════════════════════════════
✅ PASS     Configuration Check
✅ PASS     Database Operations
✅ PASS     Session Replanning Flag
✅ PASS     Missed Session Detection
✅ PASS     Frontend Schedule Fetch
✅ PASS     Replanning Agent

────────────────────────────────────────────────────────────
Results: 6/6 tests passed
────────────────────────────────────────────────────────────

🎉 ALL TESTS PASSED! Replanning system is working correctly.
```

---

## 🖥️ 5-Minute Manual UI Test

### Setup
```bash
# 1. Start the server
python app.py

# 2. Open browser
# Visit: http://localhost:5000/tracker

# 3. Open browser console (F12 → Console tab)
```

### Test Steps

1. **Check Today's Schedule**
   - Look at "Today's Study Plan" card
   - Note the sessions scheduled for today

2. **Create a Missed Session**
   - Wait for a session's end time to pass WITHOUT starting it
   - OR manually create a past session in your schedule

3. **Reload the Page**
   - Press F5 or Ctrl+R
   - Wait 2-3 seconds

4. **Verify Replanning Worked**

   ✅ **You should see:**
   - Desktop notification: "📅 Session Automatically Rescheduled"
   - Session History shows new "Incompleted" entry
   - That entry has "✓ Replanned" badge (green)
   - "Today's Study Plan" updates to show new time

   ✅ **Browser console shows:**
   ```javascript
   [Auto-Replan] Starting replanning for session 123
   [ReplanningAgent] Replanning successful. is_rescheduled=true
   [DB] Updated plan 5 with replanned timetable
   [Schedule] Fetched plan 5 for user 1, timetable has 35 sessions
   ```

   ❌ **If you see errors or nothing happens** → See troubleshooting

---

## 🔧 Common Issues & Fixes

### Issue 1: "USE_MOCK_LLM is enabled"

**Symptom:** Diagnostic shows warning about mock mode

**Fix:**
```bash
# Edit .env file
USE_MOCK_LLM=0

# Restart Flask server
```

---

### Issue 2: "AWS credentials not configured"

**Symptom:** Diagnostic shows AWS credentials NOT SET

**Fix:**
```bash
# Edit .env file, add your credentials:
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
AWS_REGION=ap-southeast-1

# Restart Flask server
```

---

### Issue 3: "No study plan found"

**Symptom:** Diagnostic shows no study plans in database

**Fix:**
1. Open http://localhost:5000
2. Log in
3. Go to "Study Plan" page
4. Click "Generate Study Plan"
5. Wait for generation to complete
6. Run diagnostic again

---

### Issue 4: "Schedule doesn't update after replanning"

**Symptom:** Notification appears but schedule shows old times

**Fix:**
This is the bug we just fixed! Make sure you have the latest code:

**Check if fix is applied:**
```bash
# Search for the fix in tracker.html
grep -n "loadSchedule()" frontend/templates/tracker.html
```

**Should show:**
```
1369:        loadSchedule();      ← Fix for auto-replan
1376:loadSchedule();              ← Initial load
1428:                loadSchedule(); ← Fix for manual replan
```

If missing, the fix wasn't applied. Re-apply the changes from `REPLANNING_FIX_SUMMARY.md`.

---

### Issue 5: Replanning agent returns error

**Symptom:** Console shows "Replanning failed: ..."

**Possible causes:**
1. **LLM API timeout** → Check internet connection
2. **Invalid AWS credentials** → Verify credentials in .env
3. **Wrong model ID** → Check AWS_BEDROCK_MODEL_ID in .env
4. **Bedrock quota exceeded** → Check AWS console
5. **Invalid timetable data** → Check database has valid JSON

**Fix:**
1. Check Flask console for full error message
2. Verify AWS credentials: `aws bedrock list-foundation-models --region ap-southeast-1`
3. Try different model ID if current one doesn't work
4. Check AWS CloudWatch logs for Bedrock errors

---

## 📊 What Each Component Does

### Backend
```
_record_missed_slots()
  ↓ Detects sessions that ended without being started
_auto_replan_missed_session()
  ↓ Calls replanning agent
evaluate_and_replan() [LLM]
  ↓ Decides how to reschedule
update_study_plan_timetable()
  ↓ Saves to database
```

### Frontend
```
Page loads
  ↓ Checks for notification
Shows notification
  ↓ Waits 500ms
loadSchedule()
  ↓ Fetches from /tracker/schedule
Display updated schedule
```

---

## 🎯 Success Criteria

Your system is working correctly if:

- ✅ `diagnose_replanning.py` → 7/7 checks pass
- ✅ `test_replanning_comprehensive.py` → 6/6 tests pass
- ✅ Manual UI test → Notification appears and schedule updates
- ✅ No errors in Flask console
- ✅ No errors in browser console

---

## 📚 Need More Help?

### Read detailed docs:
- **`REPLANNING_VERIFICATION_COMPLETE.md`** - Full system verification report
- **`REPLANNING_ARCHITECTURE.md`** - How the system works
- **`FRONTEND_BACKEND_CHECK.md`** - Detailed verification checklist
- **`TESTING_CHECKLIST.md`** - Step-by-step manual testing

### Run diagnostic tests:
```bash
# Quick health check
python diagnose_replanning.py

# Full automated test
python test_replanning_comprehensive.py

# Database-only test
python test_replanning_db.py
```

### Check logs:
```bash
# Flask server console
# Look for: [Auto-Replan], [ReplanningAgent], [DB], [Schedule]

# Browser console (F12)
# Look for: [Schedule] logs and errors
```

---

## 🚀 Ready to Go!

If all checks pass, your replanning system is fully functional!

**What happens when you miss a session:**
1. System detects the miss
2. LLM intelligently reschedules it
3. Database saves the new timetable
4. Notification tells you about the change
5. Schedule automatically updates to show new time

**No manual intervention needed!** ✨
