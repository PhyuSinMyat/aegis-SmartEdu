# SCHEDULER DEBUG - EXECUTIVE SUMMARY

## Root Cause
**`init_scheduler(app, db)` was imported but NEVER CALLED in `app.py`**

This meant the APScheduler background scheduler was initialized but never started, so no scheduled jobs would ever run.

---

## Critical Fix Applied

### **app.py** (Lines 35-43)
Added the missing scheduler initialization call in `create_app()`:

```python
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    print("[AppInit] Running in reloader process – scheduler will start in main process")
else:
    print("[AppInit] Starting scheduler in main Flask process")
    try:
        init_scheduler(app, db)  # ← THIS WAS MISSING!
        print("[AppInit] ✓ Scheduler successfully initialized")
    except Exception as exc:
        print(f"[AppInit] ✗ Failed to initialize scheduler: {exc}")
        raise
```

This handles Flask debug reloader properly (prevents double-start).

---

## Additional Improvements

### **summary_scheduler.py** - Comprehensive Logging Added
- ✅ Explicit timezone: `Asia/Singapore`
- ✅ Startup confirmation logs with next run time
- ✅ **TEMPORARY test schedule** (fires every 2 minutes) for quick debugging
- ✅ Per-user, per-session progress tracking
- ✅ Active user count logging
- ✅ Study plan existence confirmation
- ✅ Session count per weekday
- ✅ LLM call success/failure with fallback detection
- ✅ Card skip detection (already generated)
- ✅ DB upsert failure logging with full exception traces

### **test_scheduler.py** - New Manual Test Script
```bash
# Test all users
python test_scheduler.py

# Fast iteration on single user
python test_scheduler.py --user 1
```

Separates scheduler issues from summary-generation issues.

### **requirements.txt** - Dependencies Added
```
APScheduler>=3.10.0
pytz>=2024.1
```

---

## How to Verify the Fix

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the app and watch for startup messages
```bash
python app.py
```

**Expected (if fix works):**
```
[AppInit] Starting scheduler in main Flask process
[Scheduler.INIT] Initializing APScheduler...
[Scheduler.INIT] Timezone: Asia/Singapore
[Scheduler.INIT] ✓ Main job added (22:43 Singapore time)
[Scheduler.INIT]   Next run: 2026-04-13 22:43:00+08:00
[Scheduler.INIT] ⚠ TEST job added (every 2 minutes)
[Scheduler.INIT]   Next run: 2026-04-13 12:42:00+08:00
[Scheduler.INIT] ✓ APScheduler started successfully
```

### Step 3: Wait 2 minutes, then look for test job firing
```
[Scheduler.JOB FIRED] *** Daily summary generation job started ***
[Scheduler.USERS] Fetched X active user(s)
```

If you see this: **Scheduler is working!** ✓

### Step 4 (Optional): Manual test for faster iteration
```bash
python test_scheduler.py --user 1
```

This tests the summary-generation logic without waiting for cron.

---

## After Debugging: Production Cleanup

**Remove the test schedule before deploying!**

In `summary_scheduler.py`, delete the test_job section (lines 527-533):
```python
    # TEMPORARY TEST SCHEDULE: Every 2 minutes (remove after debugging)
    test_job = scheduler.add_job(...)
    logger.info(f"[Scheduler.INIT] ⚠ TEST job added...")
```

Keep only the main_job with the 22:43 production schedule.

---

## Files Changed

| File | Change | Impact |
|------|--------|--------|
| **app.py** | Added scheduler init call | ✅ CRITICAL FIX |
| **summary_scheduler.py** | Added timezone, logging | ✅ Full visibility |
| **test_scheduler.py** | New file for manual testing | ✅ Faster debugging |
| **requirements.txt** | Added APScheduler, pytz | ✅ Dependencies |
| **SCHEDULER_DEBUG_GUIDE.md** | New comprehensive guide | ✓ Reference |
| **CHANGES_SUMMARY.md** | Detailed change log | ✓ Reference |

---

## Expected Behavior After Fix

- ✅ Scheduler initializes on app startup
- ✅ Main job scheduled to run at 22:43 Singapore time daily
- ✅ Test job fires every 2 minutes (for verification)
- ✅ Each job execution is clearly logged with progress
- ✅ Any failures are logged with full exception context
- ✅ Manual testing possible via `test_scheduler.py`

---

## Common Symptoms & Fixes

| Problem | Root Cause | Check Log For |
|---------|-----------|---------------|
| `[AppInit] ✗ Failed to initialize scheduler` | Init error | Full exception message in log |
| No `[Scheduler.JOB FIRED]` after 2 min | Scheduler didn't start | Look for `[AppInit]` messages |
| `[Scheduler.USERS] Fetched 0` | No active users in DB | Insert test users |
| `⚠ No study plan found` | User has no timetable | Check user_id has study plan |
| `Found 0 session(s) for Monday` | No timetable for today | Check timetable data for today's weekday |
| `✓ Card saved to database` | Everything working! | Success ✓ |

---

## Next Steps

1. ✅ **Install dependencies**: `pip install -r requirements.txt`
2. ✅ **Test startup**: `python app.py` (look for `[AppInit]` messages)
3. ✅ **Wait for test job**: Watch for `[Scheduler.JOB FIRED]` in ~2 minutes
4. ✅ **Review logs**: Check SCHEDULER_DEBUG_GUIDE.md for what to look for
5. ✅ **Manual test**: `python test_scheduler.py --user 1` for quick iteration
6. ✅ **Clean up**: Remove test_job before production

---

## Questions?

- **"Why does the log show two startup messages?"** → Flask debug mode (normal). Scheduler only starts in main process.
- **"Can I remove the test schedule?"** → Yes! After verifying. See cleanup instructions above.
- **"The summary LLM is failing. Is the scheduler broken?"** → No, scheduler works, but LLM/Bedrock has issues. Check LLM logs separately.
- **"How do I change the time from 22:43?"** → Edit `CronTrigger(hour=22, minute=43)` in `init_scheduler()` (line 511).

---

**All changes are minimal, structured, and non-invasive to existing logic. Focus: diagnosis first, then reliable operation.**
