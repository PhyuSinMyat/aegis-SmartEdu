# Replanning Fix Testing Checklist

## Pre-Test Setup
- [ ] Server is running (`python app.py`)
- [ ] User is logged in
- [ ] User has a study plan generated
- [ ] Browser console is open (F12) to view logs

## Test Case 1: Automatic Replanning (Missed Session)

### Setup
1. [ ] Note the current time
2. [ ] Check today's study plan on the tracker page
3. [ ] Identify a study session that will end soon (or create one that's already passed)

### Test Steps
1. [ ] Wait for the session's scheduled end time to pass WITHOUT starting it
2. [ ] Reload the tracker page
3. [ ] Look for the replanning notification popup
4. [ ] Check the "Today's Study Plan" section

### Expected Results
- [ ] ✅ Desktop notification appears: "📅 Session Automatically Rescheduled"
- [ ] ✅ Console shows: `[Auto-Replan] Starting replanning for session...`
- [ ] ✅ Console shows: `[DB] Updated plan ... with replanned timetable`
- [ ] ✅ Console shows: `[Schedule] Fetched plan ... timetable has X sessions`
- [ ] ✅ Today's study plan shows the rescheduled session (different time/day)
- [ ] ✅ Session history shows "Replanned" badge next to the missed session

### ❌ Failure Indicators
- Session history shows missed session but schedule hasn't changed
- No replanning notification appears
- Console shows errors
- Schedule still shows original timetable

---

## Test Case 2: Manual Replanning Button

### Setup
1. [ ] Complete Test Case 1 OR create a missed session manually
2. [ ] Verify there's an "incompleted" session in the Session History table
3. [ ] Note the current schedule before clicking

### Test Steps
1. [ ] Find the missed session in Session History
2. [ ] Click the "Replan" button next to it
3. [ ] Wait for the spinner to complete
4. [ ] Observe the schedule section

### Expected Results
- [ ] ✅ Button changes to "✓ Replanned" badge (green)
- [ ] ✅ Desktop notification appears: "Session Replanned"
- [ ] ✅ Console shows: `[Schedule] Fetched plan ... timetable has X sessions`
- [ ] ✅ Today's study plan refreshes automatically (no manual reload needed)
- [ ] ✅ Rescheduled session appears in the schedule

### ❌ Failure Indicators
- Button stays stuck in loading state
- Alert shows "Failed to replan session"
- Schedule doesn't update (need manual page reload)

---

## Test Case 3: Database Verification (Technical)

### Test Steps
1. [ ] Open terminal/command prompt
2. [ ] Navigate to project directory
3. [ ] Run: `python test_replanning_db.py`

### Expected Output
```
✓ Found study plan: plan_id=X, title=...
✓ Original timetable has Y sessions

Original timetable:
  1. Monday 09:00-10:00: ...
  ...

✓ Modified timetable has Y+1 sessions (added 1 test session)

Updating plan X with replanned timetable...
[DB] Updated plan X with replanned timetable. Note: [TEST] Replanning test
[DB] Verified: Plan X timetable length = ... chars

✓ Retrieved updated plan: Y+1 sessions
✅ SUCCESS: Replanned session found in database!
   Monday 20:00-21:00: TEST REPLANNED SESSION

Restoring original timetable...
[DB] Updated plan X with new timetable.
[DB] Verified: Plan X timetable length = ... chars
✓ Restored: Y sessions

============================================================
Test completed successfully!
============================================================
```

### ❌ Failure Indicators
- Script crashes with error
- "❌ FAIL: Replanned session NOT found in database!"
- Timetable count doesn't increase
- Database errors appear

---

## Test Case 4: Multi-Session Replanning

### Setup
1. [ ] Create or identify 2+ sessions that will be missed today
2. [ ] Note their original times and modules

### Test Steps
1. [ ] Let multiple sessions pass without starting them
2. [ ] Reload the tracker page
3. [ ] Observe multiple replanning notifications

### Expected Results
- [ ] ✅ Each missed session gets replanned separately
- [ ] ✅ Multiple notifications may appear (one per session)
- [ ] ✅ All replanned sessions appear in the updated schedule
- [ ] ✅ No duplicate processing (console doesn't show "already replanned, skipping")

---

## Console Log Checklist

When replanning occurs, you should see these logs in order:

```
[Auto-Replan] Starting replanning for session 123, module=Mathematics
[ReplanningAgent] Replanning successful. is_rescheduled=True, explanation=...
[ReplanningAgent] Original timetable had 35 sessions, patched has 35 sessions
[Auto-Replan] Updating plan 5 with 35 sessions
[DB] Updated plan 5 with replanned timetable. Note: [Auto-replan] ...
[DB] Verified: Plan 5 timetable length = 12345 chars
[Auto-Replan] Session 123 successfully replanned and saved to database
```

When frontend loads schedule:
```
[Schedule] Fetched plan 5 for user 1, timetable has 35 total sessions
[Schedule] Today (Wednesday) has 4 sessions
```

---

## Troubleshooting

### Issue: Schedule not updating
**Check:**
- [ ] Is `loadSchedule()` being called? (Check browser console)
- [ ] Is `/tracker/schedule` endpoint returning updated data? (Check Network tab)
- [ ] Is database actually updated? (Run `test_replanning_db.py`)

### Issue: Replanning not triggering
**Check:**
- [ ] Is session marked as "incompleted"? (Check Session History)
- [ ] Is session end time in the past? (Check current time vs session time)
- [ ] Has session already been replanned? (Console: "already replanned, skipping")

### Issue: Console errors
**Check:**
- [ ] Copy full error message
- [ ] Check if LLM API is responding (replanning agent uses LLM)
- [ ] Verify database connection
- [ ] Check Flask session is working (for notification storage)

---

## Sign-Off

- [ ] All test cases passed
- [ ] Console logs show correct flow
- [ ] Database verification successful
- [ ] Replanned sessions visible in UI
- [ ] No errors or warnings in console

**Tested by:** _______________  
**Date:** _______________  
**Notes:** _______________
