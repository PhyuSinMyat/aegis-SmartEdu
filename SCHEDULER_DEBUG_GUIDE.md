# SCHEDULER DEBUG GUIDE
## Version 13.5 - Daily Summary Scheduler

### Summary of Changes Made

**Root Cause Found:**
```
❌ init_scheduler(app, db) was NEVER called in app.py
```

This meant the background scheduler was never started.

---

## Changes Implemented

### 1. **app.py** - Now initializes the scheduler
**Changes:**
- ✅ Added import: `from backend.services.summary_scheduler import init_scheduler`
- ✅ Added import: `import os` (for debug mode detection)
- ✅ Added scheduler initialization in `create_app()` (lines 35-43)
- ✅ Prevents double-start in Flask debug reloader using `WERKZEUG_RUN_MAIN` check

**Key lines:**
```python
# Lines 35-43 in app.py
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    print("[AppInit] Running in reloader process – scheduler will be started in main process")
else:
    print("[AppInit] Starting scheduler in main Flask process")
    try:
        init_scheduler(app, db)
        print("[AppInit] ✓ Scheduler successfully initialized")
    except Exception as exc:
        print(f"[AppInit] ✗ Failed to initialize scheduler: {exc}")
        raise
```

---

### 2. **summary_scheduler.py** - Comprehensive logging added

#### 2a. Added timezone support (Asia/Singapore)
```python
from pytz import timezone
singapore_tz = timezone('Asia/Singapore')
```

#### 2b. init_scheduler() improvements:
- ✅ Logs scheduler startup with clear markers
- ✅ Shows next scheduled run time for each job
- ✅ **TEMPORARY TEST SCHEDULE** (every 2 minutes) added for debugging
- ✅ Explicit timezone in CronTrigger

**To remove test schedule after debugging:**
- Delete the test_job section (lines ~520-530 in summary_scheduler.py)
- Keep only the main_job

#### 2c. run_daily_summary_job() improvements:
- ✅ Clear log markers (===) to see job fire
- ✅ Logs active user count fetched
- ✅ Per-user status logging with subsections

#### 2d. generate_summaries_for_user() improvements:
- ✅ Logs study plan retrieved
- ✅ Logs academic week computed
- ✅ Logs session count found for today
- ✅ Logs existing cards in database
- ✅ For each session:
  - Progress indicator [1/5]
  - What's being processed (subject | topic)
  - LLM call status (generated / failed / fallback)
  - Card counts (flashcards, quiz questions)
  - DB save status (✓ or ✗)
- ✅ Final summary: saved vs skipped counts

---

## How to Test the Scheduler

### Test 1: Verify Startup Messages
```bash
cd c:\ai_agent_project\version_13.5_summary_agent_crimson_removenote
python app.py
```

**Expected output:**
```
[AppInit] Starting scheduler in main Flask process
[Scheduler.INIT] Initializing APScheduler...
[Scheduler.INIT] Timezone: Asia/Singapore
[Scheduler.INIT] ✓ Main job added (22:43 Singapore time)
[Scheduler.INIT]   Next run: 2026-04-13 22:43:00+08:00
[Scheduler.INIT] ⚠ TEST job added (every 2 minutes) - REMOVE AFTER DEBUGGING!
[Scheduler.INIT]   Next run: 2026-04-13 12:42:00+08:00
[Scheduler.INIT] ✓ APScheduler started successfully
```

If you see this: **Scheduler is working!** ✓

---

### Test 2: Manual Trigger (For All Users)
Run the scheduler job manually without waiting for cron:

```bash
python test_scheduler.py
```

**Expected output:**
```
[Scheduler.JOB FIRED] *** Daily summary generation job started ***
[Scheduler.USERS] Fetched N active user(s)
[Summary.USER:1] Generating summaries for 2026-04-13 (Monday)
[Summary.USER:1] ✓ Study plan retrieved
[Summary.USER:1] Found 3 session(s) for Monday
[Summary.USER:1] [1/3] Processing: Database | Query Optimization
[Summary.USER:1]   └─ → Generating AI summary...
[Summary.USER:1]   └─ ✓ Summary generated
...etc...
[Summary.USER:1]   └─ ✓ Card saved to database
[Scheduler.COMPLETE] Daily summary job finished. Total cards saved: 3
```

---

### Test 3: Manual Trigger (Single User Quick Test)
For fast iteration on a single user:

```bash
python test_scheduler.py --user 1
```

This tests generation logic **without** involving the scheduler.

---

### Test 4: Verify Test Schedule Fires Every 2 Minutes
The test job is set to run every 2 minutes. Watch the logs:

1. Run `python app.py`
2. Wait 2 minutes
3. Look for:
```
[Scheduler.JOB FIRED] *** Daily summary generation job started ***
```

This proves APScheduler is working correctly.

---

## Diagnostic Questions to Answer

When things don't work, check logs for answers to:

1. **Does the scheduler start?**
   - Look for: `[AppInit] ✓ Scheduler successfully initialized`
   - If missing: scheduler import failed or exception during init

2. **Does the test job fire every 2 minutes?**
   - Look for: `[Scheduler.JOB FIRED]` appearing periodically
   - If missing: APScheduler didn't start or has no jobs

3. **Can the job fetch users?**
   - Look for: `[Scheduler.USERS] Fetched N active user(s)`
   - If N=0: no active users in database

4. **Can the job find the study plan?**
   - Look for: `[Summary.USER:X] ✓ Study plan retrieved`
   - If missing: `⚠ No study plan found` means DB query failed or user has no plan

5. **Are sessions found for today?**
   - Look for: `Found X session(s) for Monday` etc
   - If 0: either no sessions scheduled for this weekday, or timetable_json is empty

6. **Are cards being skipped (already exist)?**
   - Look for: `⊘ SKIPPED (already fully generated)`
   - If all cards skipped, no new cards will be saved

7. **Do LLM calls succeed?**
   - Look for: `✓ Summary generated` vs `⚠ Summary LLM failed`
   - If failed: check Bedrock/LLM service connection

8. **Do DB saves succeed?**
   - Look for: `✓ Card saved to database` vs `✗ DB upsert FAILED`
   - `✗ FAILED` shows the actual error

---

## After Debugging: Clean Up

**IMPORTANT: Remove test schedule before deploying!**

In `summary_scheduler.py`, around line 526-530, delete:
```python
    # TEMPORARY TEST SCHEDULE: Every 2 minutes (remove after debugging)
    test_job = scheduler.add_job(...)
    logger.info(f"[Scheduler.INIT] ⚠ TEST job added (every 2 minutes)...")
    logger.info(f"[Scheduler.INIT]   Next run: {test_job.next_run_time}")
```

Keep only the main_job with the production schedule (22:43).

---

## Troubleshooting Matrix

| Symptom | Likely Root Cause | Check |
|---------|-------------------|-------|
| `[AppInit] ✗ Failed to initialize scheduler` | Import or init error | Full exception in logs |
| No `[Scheduler.JOB FIRED]` after 2 min | Scheduler not started | Check `[AppInit]` logs |
| `[Scheduler.USERS] Fetched 0` | No active users in DB | Insert test users |
| `⚠ No study plan found` | User has no study plan | Upload timetable for user |
| `Found 0 session(s)` | No timetable for today's weekday | Check timetable data |
| `⚠ Summary LLM failed` | LLM/Bedrock unavailable | Check API credentials |
| `✗ DB upsert FAILED` | Database error | Check full exception in logs |

---

## Flask Debug Mode Note

Running with `debug=True` in Flask starts the app twice:
1. **Reloader process** (development watcher) - scheduler won't start here
2. **Main process** - scheduler starts here

You'll see both startup messages. This is **normal and expected**.

If you want test schedule to NOT fire before integration:
- Remove `test_job` section from `init_scheduler()`
- Keep only `main_job` with 22:43 schedule
- This is temporary; only for development

---

## Production Deployment Checklist

- [ ] Remove test_job from summary_scheduler.py
- [ ] Set correct timezone if not Singapore
- [ ] Set correct time in CronTrigger (currently 22:43, which is 10:43 PM)
- [ ] Ensure Flask runs with `debug=False`
- [ ] Check logs show `[Scheduler.COMPLETE]` appearing once daily
- [ ] Verify DB queries complete without errors
- [ ] Test LLM/Bedrock connectivity
- [ ] Monitor logs daily for first 3 days post-deployment
