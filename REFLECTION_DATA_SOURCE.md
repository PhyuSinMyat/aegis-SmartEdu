# Reflection Page - Data Sources

## Important: No Dedicated Reflection Table!

The Reflection page does **NOT have its own database table**. Instead, it **aggregates data from existing tables** in real-time when you load the page.

---

## How Reflection Data Works

### Data is CALCULATED, not STORED

```
User visits Reflection page for Week 11
           ↓
Backend queries multiple tables
           ↓
Calculates metrics on-the-fly
           ↓
Returns JSON to frontend
           ↓
Frontend displays the data
```

**Key Point:** Reflection data is **computed dynamically** each time you load the page.

---

## Data Sources for Each Section

### 1. Week Stats (Top Cards)
**Function:** `get_reflection_week_stats(user_id, week_number)`

**Sources:**
```sql
study_plans.timetable_json
  ↓ Planned hours, sessions scheduled

study_sessions (WHERE status='completed')
  ↓ Completed hours, sessions done

study_sessions (WHERE status!='completed')  
  ↓ Missed sessions, missed hours

CALCULATION:
  completion_rate = (completed_hours / planned_hours) * 100
```

**Tables Used:**
- `study_plans` - Planned study time
- `study_sessions` - Actual study activity

---

### 2. Daily Study Hours Chart
**Function:** `get_daily_hours_for_week(user_id, week_number)`

**Sources:**
```sql
study_plans.timetable_json
  ↓ Planned hours per day (from time slots)

study_sessions (GROUP BY date)
  ↓ Completed hours per day (SUM study_seconds)
```

**Tables Used:**
- `study_plans` - Daily planned hours
- `study_sessions` - Daily completed hours

---

### 3. Module Progress
**Function:** `get_reflection_module_stats(user_id, week_number)`

**Sources:**
```sql
study_plans.timetable_json (subject field)
  ↓ Planned hours per module

study_sessions (GROUP BY module_name)
  ↓ Completed hours per module

CALCULATION:
  completion_rate = (completed_hours / planned_hours) * 100
```

**Tables Used:**
- `study_plans` - Module planned hours
- `study_sessions` - Module completed hours

---

### 4. Study Patterns
**Function:** `get_reflection_study_patterns(user_id, week_number)`

**Sources:**
```sql
study_sessions (ORDER BY actual_start)
  ↓ Time periods, completion status, sequences

CALCULATIONS:
- Peak Performance: GROUP BY time_period, calculate completion rate
- Average Duration: Find consecutive completed sequences, average total
- Most Productive: GROUP BY day_of_week, count completed
- Struggle Period: GROUP BY time_period, count incomplete
```

**Tables Used:**
- `study_sessions` only

---

### 5. Performance Highlights
**Function:** `get_reflection_performance_highlights(user_id, week_number)`

**Sources:**
```sql
quiz_results
JOIN daily_summary_cards
  ↓ Module names, quiz scores

CALCULATION:
  avg_score = AVG(correct_count / question_count * 100)
  GROUP BY module_name
```

**Tables Used:**
- `quiz_results` - Quiz scores
- `daily_summary_cards` - Module names

---

## Example: How Week 11 Data is Generated

When you view Week 11 on the Reflection page:

### Step 1: Calculate Date Range
```python
semester_start = '2026-02-02'  # from study_preferences
week_11_start = semester_start + (10 weeks) = '2026-04-13'
week_11_end = week_11_start + 6 days = '2026-04-19'
```

### Step 2: Query study_plans
```sql
SELECT timetable_json FROM study_plans
WHERE user_id = 1
  AND title LIKE '%Week 11%'
ORDER BY created_at DESC
LIMIT 1
```
**Result:** Gets the latest Week 11 study plan
**Parses:** All time slots → calculates planned hours per module/day

### Step 3: Query study_sessions
```sql
SELECT * FROM study_sessions
WHERE user_id = 1
  AND DATE(actual_start) BETWEEN '2026-04-13' AND '2026-04-19'
```
**Result:** All study sessions in that week
**Calculates:** Completed hours, missed sessions, patterns

### Step 4: Query quiz_results
```sql
SELECT q.*, s.subject
FROM quiz_results q
JOIN daily_summary_cards s ON q.summary_id = s.summary_id
WHERE q.user_id = 1
  AND DATE(q.created_at) BETWEEN '2026-04-13' AND '2026-04-19'
```
**Result:** All quizzes taken that week
**Calculates:** Average scores per module

### Step 5: Combine & Return
```json
{
  "week_number": 11,
  "stats": { "planned_hours": 20, "completed_hours": 8, ... },
  "daily_hours": [ {"day": "Mon", "planned": 2, "completed": 1}, ... ],
  "module_stats": [ {"module_name": "Database", "completion_rate": 40}, ... ],
  "study_patterns": { "peak_performance": {...}, ... },
  "performance_highlights": { "strongest": {...}, ... }
}
```

---

## Why No Reflection Table?

### Pros of Current Approach (No Dedicated Table):
✅ **Always up-to-date** - Data reflects latest study_sessions/quiz_results  
✅ **No duplication** - Same data isn't stored twice  
✅ **Flexible** - Can change calculations without migrating data  
✅ **No sync issues** - Can't get out of sync with source tables  
✅ **Less storage** - No redundant data

### Cons of Current Approach:
❌ **Calculation overhead** - Computes on every page load  
❌ **No historical snapshots** - Can't see "what did Week 11 look like back then?"  
❌ **Performance** - Slower with large datasets

---

## Where the Data Actually Lives

```
Reflection Page Display:
├─ Planned Hours
│  └─ Source: study_plans.timetable_json
│
├─ Completed Hours  
│  └─ Source: study_sessions.study_seconds (WHERE status='completed')
│
├─ Module Progress
│  ├─ Planned: study_plans.timetable_json (subject field)
│  └─ Completed: study_sessions (GROUP BY module_name)
│
├─ Study Patterns
│  └─ Source: study_sessions (time analysis)
│
└─ Performance Highlights
   └─ Source: quiz_results + daily_summary_cards
```

---

## Implications

### When Data Changes:
```
You complete a study session
         ↓
study_sessions table updated
         ↓
Refresh Reflection page
         ↓
NEW calculation includes the session
         ↓
Reflection stats updated automatically
```

### Week-to-Week Comparison:
The reflection page shows **what the data looks like NOW** for each week, not **what it looked like when you originally studied that week**.

Example:
```
Week 11 (April 13-19):
- Original: 5 completed sessions
- You add 2 more sessions later (backdated)
- Reflection page NOW shows: 7 completed sessions for Week 11
```

---

## Should You Add a Reflection Table?

### Consider Adding If:
- You want historical snapshots ("Week 11 had 80% completion on May 1st")
- You're experiencing performance issues with calculations
- You want to track changes over time ("Week 11 improved from 60% → 80%")

### Current Design is Fine If:
- You only care about current state of data
- Dataset is small enough for fast calculations
- You prefer data consistency (no sync issues)
- You want flexibility to change metrics

---

## Database Tables Actually Used

| Table | Purpose in Reflection |
|-------|----------------------|
| `study_plans` | Planned hours, timetable structure |
| `study_sessions` | Completed hours, patterns, missed sessions |
| `study_preferences` | Semester start date (for week calculations) |
| `quiz_results` | Quiz scores for performance highlights |
| `daily_summary_cards` | Module names for quiz results |

**Total: 5 tables** dynamically queried and aggregated.

---

## Summary

✅ **Reflection page has NO dedicated table**  
✅ **All data is calculated on-the-fly from existing tables**  
✅ **Data is always current (not historical snapshots)**  
✅ **5 source tables: study_plans, study_sessions, study_preferences, quiz_results, daily_summary_cards**  
✅ **Functions perform aggregations and return JSON**  

This is actually a **good design** for most use cases - it keeps your database normalized and prevents data duplication!
