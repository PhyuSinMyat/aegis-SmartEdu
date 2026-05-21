# Replanning Architecture & Data Flow

## Overview
The replanning system automatically reschedules missed study sessions based on their importance and urgency.

## Key Components

### 1. Replanning Agent (`backend/agents/replanning_agent.py`)
**Purpose:** Uses LLM to intelligently decide how to handle missed sessions

**Input:**
- Current weekly timetable (JSON array)
- Missed session details (module, duration, time)

**Output:**
```json
{
  "patched_timetable": [...],  // Updated timetable with rescheduled session
  "explanation": "Session merged with Thursday slot",
  "is_rescheduled": true
}
```

**Logic:**
1. Analyzes importance (upcoming class? assessment? revision?)
2. Decides action (reschedule soon, merge, skip, push later)
3. Returns minimal changes to timetable
4. Keeps schedule realistic (no overloaded days)

---

### 2. Database Layer (`database.py`)

#### Key Functions

**`update_study_plan_timetable(plan_id, new_timetable_json, append_text)`**
- Updates the `timetable_json` column in `study_plans` table
- Optionally appends a note to `plan_text`
- Used by both automatic and manual replanning

**`is_session_replanned(session_id)`**
- Checks if session has a 'replanned' event in `session_events` table
- Prevents duplicate replanning processing

**`log_session_event(session_id, user_id, event_type, description)`**
- Records replanning events for audit trail
- Event type: "replanned"

---

### 3. Tracker Routes (`backend/routes/tracker_routes.py`)

#### Automatic Replanning Flow

**`_record_missed_slots(user_id)`** (Line 175)
- Called on every tracker page load
- Scans today's schedule for past slots
- Creates "incompleted" session if no record exists
- Triggers `_auto_replan_missed_session()` for each miss

**`_auto_replan_missed_session(session_id, user_id, missed_data, current_plan)`** (Line 131)
- Checks if already replanned (avoid duplicates)
- Calls replanning agent
- Updates database if rescheduled
- Stores notification in Flask session for next page load

**`get_schedule()`** (Line 625)
- Returns today's sessions from the current plan
- Frontend calls this to display schedule
- Always fetches fresh data from database

#### Manual Replanning Flow

**`POST /tracker/session/<id>/replan`** (Line 460)
- Triggered by "Replan" button in UI
- Validates session is "incompleted" and not already replanned
- Calls replanning agent
- Updates database and logs event
- Returns success/error JSON

---

### 4. Frontend (`frontend/templates/tracker.html`)

#### Schedule Display

**`loadSchedule()`** (Line 932)
- Fetches `/tracker/schedule` endpoint
- Renders today's sessions
- Shows countdown to next session
- Called on page load

#### Replanning Notification

**Auto-replan notification handler** (Line 1338)
- Runs when `replan_notification` exists in Flask session
- Shows desktop notification
- **CRITICAL:** Calls `loadSchedule()` after 500ms to refresh schedule

**Manual replan button handler** (Line 1405)
- Sends POST to `/tracker/session/<id>/replan`
- Shows spinner during processing
- **CRITICAL:** Calls `loadSchedule()` after success to refresh schedule
- Replaces button with "Replanned" badge

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER MISSES SESSION                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ User reloads tracker page                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ _record_missed_slots() scans today's schedule               │
│  - Finds slots where end_time < now                         │
│  - Checks if session record exists                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Creates "incompleted" session in database                   │
│  - Status: "incompleted"                                    │
│  - Study time: 0 seconds                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ _auto_replan_missed_session() triggered                     │
│  - Check: is_session_replanned? → Skip if yes              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Replanning Agent (LLM)                                      │
│  Input: current_timetable, missed_session                   │
│  Output: patched_timetable, explanation, is_rescheduled     │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌─────────────────┐   ┌─────────────────┐
│ is_rescheduled  │   │ Not rescheduled │
│     = True      │   │  (low priority) │
└────────┬────────┘   └────────┬────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│ db.update_study_plan_timetable(plan_id, patched_timetable) │
│  - Updates timetable_json column                            │
│  - Adds note to plan_text                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ db.log_session_event(session_id, "replanned", explanation) │
│  - Records event in session_events table                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ session["pending_replan_notification"] = {...}              │
│  - Stores notification for next page load                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Page finishes loading, renders template                     │
│  - replan_notification passed to JavaScript                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ JavaScript: Show desktop notification                        │
│  "📅 Session Automatically Rescheduled"                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ ★ NEW FIX: setTimeout(() => loadSchedule(), 500)           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ fetch('/tracker/schedule')                                  │
│  - Fetches updated timetable from database                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Display updated schedule in UI                              │
│  - Shows rescheduled sessions                               │
│  - User sees the replanned timetable                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### `study_plans`
```sql
plan_id          INTEGER PRIMARY KEY
user_id          INTEGER
title            TEXT
plan_text        TEXT              -- LLM-generated explanation
timetable_json   TEXT              -- JSON array of sessions (UPDATED BY REPLANNING)
created_at       TIMESTAMP
```

### `study_sessions`
```sql
session_id       INTEGER PRIMARY KEY
user_id          INTEGER
module_name      TEXT
status           TEXT              -- "active", "completed", "incompleted"
study_seconds    INTEGER
...
```

### `session_events`
```sql
event_id         INTEGER PRIMARY KEY
session_id       INTEGER
user_id          INTEGER
event_type       TEXT              -- "started", "ended", "replanned"
description      TEXT
created_at       TIMESTAMP
```

---

## The Fix Explained

### Problem
- Backend saved replanned timetable to database ✅
- Frontend loaded schedule once on page load ✅
- Frontend never refreshed schedule after replanning ❌

### Solution
**After replanning completes, trigger `loadSchedule()` to fetch updated data**

#### Location 1: Automatic replanning notification (tracker.html:1365-1370)
```javascript
setTimeout(() => {
    loadSchedule();  // ← Refresh schedule from database
}, 500);
```

#### Location 2: Manual replan button (tracker.html:1418-1421)
```javascript
if (resp.ok && data.ok) {
    // ... show success badge ...
    setTimeout(() => {
        loadSchedule();  // ← Refresh schedule from database
    }, 500);
}
```

### Why 500ms delay?
- Ensures database commit completes
- Prevents race condition where frontend fetches before backend writes
- Gives time for Flask session to be saved

---

## Debugging Tips

### Check if replanning happened
```bash
# Look for these logs in Flask console:
[Auto-Replan] Starting replanning for session 123
[ReplanningAgent] Replanning successful. is_rescheduled=True
[DB] Updated plan 5 with replanned timetable
```

### Check if frontend fetched updated schedule
```javascript
// Look for these logs in browser console:
[Schedule] Fetched plan 5 for user 1, timetable has 35 sessions
[Schedule] Today (Wednesday) has 4 sessions
```

### Check database directly
```bash
python test_replanning_db.py
```

### Check session events
```sql
SELECT * FROM session_events 
WHERE session_id = 123 
AND event_type = 'replanned';
```

---

## Future Enhancements

1. **Real-time updates** (WebSocket)
   - Push replanned timetable to frontend without page reload
   - Show live notification when replanning completes

2. **Undo replanning**
   - Store previous timetable version
   - Allow user to revert unwanted changes

3. **Replanning history**
   - Show timeline of all replanning actions
   - Visualize how schedule evolved over time

4. **Batch replanning**
   - Handle multiple missed sessions together
   - Optimize schedule holistically instead of one-by-one

5. **User preferences**
   - Let user configure replanning behavior
   - Set priority rules per module
