# Study Patterns Update - Reflection Page

## What Changed

The **Study Patterns** section on the Reflection page now displays **real data** from study sessions instead of hard-coded values.

## Features Implemented

### 1. Peak Performance 🏆
**Shows:** Time slot with highest completion rate

**Logic:**
- Groups all sessions by time period (Morning/Afternoon/Evening/Night)
- Calculates completion rate for each period
- Displays the period with best performance
- Shows actual time range (e.g., "9:00 - 11:00 AM")

**Example Output:**
```
PEAK PERFORMANCE
8:00 PM - 9:00 PM
100% completion rate
```

---

### 2. Average Duration ⏱️
**Shows:** Average length of consecutive completed session sequences (concentration span)

**Logic:**
- Finds sequences of consecutive completed sessions
- A sequence breaks when a session is missed/incomplete
- Calculates total duration of each sequence
- Averages across all sequences

**Example:**
```
Sessions: ✓1h → ✓1.5h → ✗missed → ✓1h → ✓1h
Sequences: [2.5h, 2h]
Average: 2h 15min
```

**Example Output:**
```
AVERAGE DURATION
55min
Average of 1 study sequence
```

**Purpose:** Measures concentration stamina - how long you can keep studying before burning out.

---

### 3. Most Productive Day 📅
**Shows:** Day of the week with most completed sessions

**Logic:**
- Groups completed sessions by day name (Monday-Sunday)
- Counts completions per day
- Shows the day with highest count

**Example Output:**
```
MOST PRODUCTIVE
Thursday
1 session completed
```

---

### 4. Struggle Period ⚠️
**Shows:** Time slot where user most often fails to complete sessions

**Logic:**
- Groups incomplete/missed sessions by time period
- Finds the period with most failures
- Shows actual time range

**Example Output:**
```
STRUGGLE PERIOD
6:00 PM - 8:00 PM
4 sessions missed
```

**Purpose:** Identifies when you need to adjust your schedule or take breaks.

---

## Technical Implementation

### Database Function
**File:** `database.py`
**Function:** `get_reflection_study_patterns(user_id, week_number)`

**Returns:**
```python
{
    'peak_performance': {
        'time_slot': '8:00 PM - 9:00 PM',
        'period': 'Evening',
        'completion_rate': 100
    },
    'average_duration': {
        'minutes': 55,
        'target_minutes': 60,
        'formatted': '55min',
        'sequences_count': 1
    },
    'most_productive': {
        'day': 'Thursday',
        'completed_sessions': 1
    },
    'struggle_period': {
        'time_slot': '6:00 PM - 8:00 PM',
        'period': 'Evening',
        'missed_sessions': 4
    }
}
```

### Data Source
**Table:** `study_sessions`

**Key Fields:**
- `actual_start` - Session start time (used for time period analysis)
- `status` - 'completed' vs 'incompleted'/'missed'/etc.
- `study_seconds` - Actual study duration (for concentration span)
- `planned_duration_mins` - Target duration (for comparison)

### Time Periods
- **Morning:** 6:00 AM - 12:00 PM
- **Afternoon:** 12:00 PM - 6:00 PM
- **Evening:** 6:00 PM - 12:00 AM (Midnight)
- **Night:** 12:00 AM - 6:00 AM

---

## Frontend Integration

### Template Changes
**File:** `frontend/templates/reflection.html`

- Added dynamic elements with IDs for updating
- JavaScript function `renderStudyPatterns(patterns)` populates data
- Updates automatically when switching weeks

### API Changes
**File:** `app.py`

- Added `study_patterns` to initial page load
- Added `study_patterns` to `/api/reflection/week/<week_number>` endpoint
- Data updates when user navigates between weeks

---

## Testing

### Test with Real Data
```bash
python test_study_patterns.py
```

### Create Sample Sessions
The system works with your existing `study_sessions` data. As you:
- ✅ Complete study sessions → Peak Performance and Most Productive update
- ❌ Miss/skip sessions → Struggle Period updates
- 📊 Build study sequences → Average Duration calculates concentration span

---

## Benefits

✅ **Personalized insights** - Shows YOUR actual study patterns  
✅ **Actionable data** - Identifies best/worst times for studying  
✅ **Concentration tracking** - Measures how long you can focus  
✅ **Pattern recognition** - Helps optimize study schedule  
✅ **Weekly comparison** - Track improvement over time

---

## Example Scenarios

### Scenario 1: Morning Person
```
Peak Performance: 9:00 - 11:00 AM (100% completion)
Most Productive: Monday
Struggle Period: 2:00 - 4:00 PM (3 sessions missed)

💡 Insight: Schedule hard subjects in the morning!
```

### Scenario 2: Night Owl
```
Peak Performance: 8:00 PM - 10:00 PM (95% completion)
Average Duration: 2h 30min
Struggle Period: 7:00 - 9:00 AM (5 sessions missed)

💡 Insight: Don't fight your natural rhythm - study at night!
```

### Scenario 3: Needs Breaks
```
Average Duration: 45min (across 8 sequences)
Peak Performance: Morning (80% completion)

💡 Insight: Take breaks every 45min to maintain performance!
```
