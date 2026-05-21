# Replanning Frontend Display Fix

## Problem
Replanned sessions were successfully stored in the database but never appeared in the frontend UI. The tracker page always showed the original timetable instead of the updated replanned timetable.

## Root Cause
The frontend JavaScript loaded the schedule **once** on page load and never refreshed it after replanning occurred. When the replanning agent updated the database with a new timetable, the frontend continued to display the stale cached schedule.

## Solution

### 1. **Frontend Schedule Refresh (tracker.html)**
Added automatic schedule reloading after replanning notifications:

#### Automatic Replanning (lines 1365-1370)
```javascript
// CRITICAL FIX: Reload the schedule to display the replanned timetable
setTimeout(() => {
    loadSchedule();
}, 500);
```
- When the page loads and detects a replanning notification, it waits 500ms then reloads the schedule
- This ensures the updated timetable is fetched from the database and displayed

#### Manual Replanning Button (lines 1418-1421)
```javascript
// CRITICAL FIX: Reload the schedule to display the replanned timetable
setTimeout(() => {
    loadSchedule();
}, 500);
```
- When the user manually clicks "Replan" on a missed session, the schedule refreshes after success
- The 500ms delay ensures the database update completes before fetching

### 2. **Debug Logging Added**

#### Database Layer (database.py:861-879)
```python
print(f"[DB] Updated plan {plan_id} with replanned timetable. Note: {append_text}")
print(f"[DB] Verified: Plan {plan_id} timetable length = {len(row[0])} chars")
```

#### Replanning Agent (replanning_agent.py:80-82)
```python
print(f"[ReplanningAgent] Replanning successful. is_rescheduled={result.get('is_rescheduled')}")
print(f"[ReplanningAgent] Original timetable had {len(current_timetable)} sessions, patched has {len(result.get('patched_timetable', []))} sessions")
```

#### Tracker Routes (tracker_routes.py:137-171)
```python
print(f"[Auto-Replan] Starting replanning for session {session_id}")
print(f"[Auto-Replan] Updating plan {current_plan['plan_id']} with {len(patched)} sessions")
print(f"[Auto-Replan] Session {session_id} successfully replanned and saved to database")
```

#### Schedule Endpoint (tracker_routes.py:632-648)
```python
print(f"[Schedule] Fetched plan {plan.get('plan_id')} for user {user_id}, timetable has {len(plan['timetable_json'])} total sessions")
print(f"[Schedule] Today ({today_name}) has {len(today_sessions)} sessions")
```

These logs help diagnose:
- Whether replanning is being triggered
- Whether the database update succeeds
- What timetable data the frontend receives
- Session count before and after replanning

## Testing

### Manual Test
1. Create a study session that will be missed
2. Miss the session (don't start it before the scheduled time passes)
3. Reload the tracker page
4. Verify:
   - ✅ Replanning notification appears
   - ✅ Schedule shows the updated timetable with the rescheduled session
   - ✅ Console logs show the replanning flow

### Automated Test
Run `test_replanning_db.py`:
```bash
python test_replanning_db.py
```

This verifies:
- ✅ Timetable can be updated in database
- ✅ Updated timetable can be retrieved
- ✅ No data loss or corruption

## Flow Diagram

```
Missed Session Detected (page load)
    ↓
_record_missed_slots() creates "incompleted" session
    ↓
_auto_replan_missed_session() called
    ↓
Replanning Agent evaluates importance
    ↓
db.update_study_plan_timetable() saves to database
    ↓
db.log_session_event() marks as "replanned"
    ↓
session["pending_replan_notification"] stores notification
    ↓
Page renders with notification
    ↓
JavaScript shows notification popup
    ↓
★ NEW: JavaScript calls loadSchedule() after 500ms ★
    ↓
/tracker/schedule endpoint fetches updated timetable from database
    ↓
Frontend displays replanned timetable
```

## Files Modified

1. **frontend/templates/tracker.html**
   - Added `loadSchedule()` call after automatic replanning notification (line 1365-1370)
   - Added `loadSchedule()` call after manual replan button (line 1418-1421)

2. **database.py**
   - Added debug logging to `update_study_plan_timetable()` (line 861-879)

3. **backend/agents/replanning_agent.py**
   - Added debug logging to `evaluate_and_replan()` (line 80-82)

4. **backend/routes/tracker_routes.py**
   - Added debug logging to `_auto_replan_missed_session()` (line 137-171)
   - Added debug logging to `get_schedule()` (line 632-648)

5. **test_replanning_db.py** (NEW)
   - Test script to verify database operations

## Expected Behavior After Fix

### Before Fix
- ❌ Replanning agent works and saves to database
- ❌ Database contains correct replanned timetable
- ❌ Frontend UI shows **original** timetable (stale)
- ❌ User never sees the rescheduled sessions

### After Fix
- ✅ Replanning agent works and saves to database
- ✅ Database contains correct replanned timetable
- ✅ Frontend UI shows **updated** timetable (fresh from database)
- ✅ User sees rescheduled sessions immediately after page reload
- ✅ Console logs show complete replanning flow for debugging

## Notes

- The fix relies on page reload to display replanned timetable (by design)
- If user stays on same page without reloading, they won't see updates until next visit
- For real-time updates without reload, would need WebSocket or polling mechanism (future enhancement)
- The 500ms delay in `setTimeout` ensures database commit completes before fetch
