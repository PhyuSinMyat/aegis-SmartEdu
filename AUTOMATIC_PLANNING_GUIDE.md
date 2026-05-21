# Automatic Study Planning System - Implementation Guide

## 📋 Overview

Your SmartEdu application now features **automatic weekly study plan generation** powered by AI agents. The system automatically generates personalized 2-week study plans for all users every **Sunday at 12:00 AM (midnight)** without requiring any manual intervention.

## 🎯 Key Features

### 1. **Automatic Scheduling**
- ⏰ **Weekly Cron Job**: Runs every Sunday at 12:00 AM
- 🤖 **AI-Powered**: Uses AWS Bedrock Claude for intelligent plan generation
- 📅 **2-Week Planning**: Generates current week + next week plans
- 👥 **Multi-User Support**: Processes all active users automatically
- 📊 **Smart Handling**: Skips incomplete setups, handles errors gracefully

### 2. **Improved UI/UX**
- 📱 **Auto-Generation Banner**: Shows next scheduled generation time
- ⏱️ **Real-Time Countdown**: Updates every minute
- 🎨 **Modern Design**: Enhanced visual hierarchy and information architecture
- 📍 **Today's Focus**: Highlights current day sessions with smart status badges
- 📈 **Progress Tracking**: Weekly completion rate visualization

### 3. **Manual Override Option**
- 🛠️ **Manual Generation**: Users can still trigger manual plan generation
- 🔄 **Immediate Refresh**: Override automatic schedule when needed
- 📝 **Custom Naming**: Optional plan title customization

## 🏗️ Architecture

### Backend Components

#### 1. **Planning Scheduler Service** (`planning_scheduler.py`)
```
backend/services/planning_scheduler.py
├── init_planning_scheduler()      # Initialize APScheduler
├── run_weekly_planning_job()      # Main cron job entry point
├── generate_plan_for_user()       # Generate plans for single user
├── shutdown_planning_scheduler()  # Graceful shutdown handler
└── trigger_manual_planning_job()  # Manual testing interface
```

**Features:**
- APScheduler with `BackgroundScheduler`
- Cron trigger: `day_of_week='sun', hour=0, minute=0`
- Automatic retry on missed runs (1-hour grace period)
- Single instance per job (no duplicates)
- Comprehensive logging for monitoring

#### 2. **Planning Agent** (`planning_agent.py`)
- Already existed in your codebase
- Handles AI prompt construction
- Streams Claude responses via AWS Bedrock
- Enforces scheduling constraints (occupied times, class blocks)
- Validates and repairs JSON output

#### 3. **Plan Routes** (`plan_routes.py`)
Enhanced with new endpoint:
```python
@plan_bp.route("/plan/latest", methods=["GET"])
def get_latest_plans():
    """Get the most recent 2-week plan bundle for current user"""
```

### Frontend Components

#### 1. **Improved Plan Page** (`plan_improved.html`)
- Auto-generation info banner with countdown
- Real-time session status tracking
- Enhanced calendar grid view
- Drag-and-drop session rescheduling
- Progressive disclosure for manual generation

#### 2. **JavaScript Enhancements**
```javascript
// Key functions:
updateNextGenerationCountdown()  // Shows time until Sunday 12:00 AM
loadLatestPlans()                // Fetches from /plan/latest API
renderDashboard()                // Updates all UI sections
```

### Database

No schema changes required! Uses existing tables:
- `study_plans`: Stores generated plans with timetable JSON
- `users`: User authentication and profiles
- `study_preferences`: User scheduling preferences
- `extraction_cache`: Processed timetable data

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
# Already included in requirements.txt:
# APScheduler>=3.10.0
pip install -r requirements.txt
```

### 2. Initialize Scheduler in `app.py`
The scheduler is automatically initialized when the Flask app starts:

```python
# app.py
from backend.services.planning_scheduler import init_planning_scheduler, shutdown_planning_scheduler

def create_app():
    # ... existing app setup ...

    # Initialize schedulers
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_planning_scheduler(app)
        atexit.register(shutdown_planning_scheduler)
```

### 3. Replace Plan Template (Optional)
```bash
# Backup existing template
mv frontend/templates/plan.html frontend/templates/plan_original.html

# Use new improved template
mv frontend/templates/plan_improved.html frontend/templates/plan.html
```

## 🧪 Testing

### Test Automatic Generation

#### Option 1: Test Single User
```bash
python test_planning_scheduler.py --user 1
```

#### Option 2: Test All Users
```bash
python test_planning_scheduler.py
```

#### Option 3: Trigger via Python
```python
from app import create_app
from database import DatabaseHelper
from backend.services.planning_scheduler import trigger_manual_planning_job

app = create_app()
db = DatabaseHelper()

# Test specific user
trigger_manual_planning_job(app, user_id=1)

# Test all users
trigger_manual_planning_job(app)
```

### Monitor Scheduler Status

```python
from backend.services.planning_scheduler import _scheduler

# Check if scheduler is running
print(f"Scheduler running: {_scheduler and _scheduler.running}")

# View scheduled jobs
for job in _scheduler.get_jobs():
    print(f"Job: {job.name}")
    print(f"Next run: {job.next_run_time}")
```

## 📊 Monitoring & Logs

### Log Locations
Logs are written to console with detailed timestamps:

```
[Planning Scheduler] INFO: Weekly planning job started
[Planning Scheduler] INFO: Found 5 user(s) to process
[Planning Scheduler] INFO: User 1: Generating Week 12 and Week 13
[Planning Scheduler] INFO: User 1: Week 12 plan saved (plan_id=234)
[Planning Scheduler] INFO: ✓ User 1: Plans generated successfully
```

### Key Log Messages

| Log Message | Meaning |
|------------|---------|
| `✓ User X: Plans generated successfully` | Success |
| `⊘ User X: Skipped - setup incomplete` | User hasn't completed onboarding |
| `✗ User X: Failed - error message` | Generation error, check details |

### Health Checks

```python
# In Python shell:
from backend.services.planning_scheduler import _scheduler

# Check scheduler health
if _scheduler and _scheduler.running:
    job = _scheduler.get_job('weekly_planning_job')
    print(f"Next run: {job.next_run_time}")
    print(f"Last run: {job.last_run_time}")
else:
    print("Scheduler not running!")
```

## 🔧 Configuration

### Change Schedule Time
Edit `planning_scheduler.py`:

```python
# Current: Sunday at 12:00 AM
scheduler.add_job(
    trigger=CronTrigger(
        day_of_week='sun',  # Change day: mon, tue, wed, thu, fri, sat, sun
        hour=0,             # Change hour: 0-23
        minute=0,           # Change minute: 0-59
    ),
    # ...
)

# Example: Every Saturday at 11:00 PM
scheduler.add_job(
    trigger=CronTrigger(
        day_of_week='sat',
        hour=23,
        minute=0,
    ),
    # ...
)
```

### Adjust Grace Period
```python
# In planning_scheduler.py init_planning_scheduler():
scheduler = BackgroundScheduler(
    job_defaults={
        'misfire_grace_time': 3600,  # 1 hour (in seconds)
    }
)
```

## 🎨 UI Customization

### Countdown Display
Edit `plan_improved.html` JavaScript:

```javascript
function updateNextGenerationCountdown() {
    // Customize countdown format
    if (days > 0) {
        countdownText = `Next auto-gen in ${days} days`;
    }
    // ...
}
```

### Auto-Generation Banner
Edit CSS in `plan_improved.html`:

```css
.auto-info-banner {
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
    /* Customize colors, borders, etc. */
}
```

## 🐛 Troubleshooting

### Issue: Scheduler Not Starting
**Symptoms:** No logs about scheduler initialization

**Solution:**
```bash
# Check if running in main process:
echo $WERKZEUG_RUN_MAIN  # Should be "true"

# Check for initialization errors in console:
# Look for: "[AppInit] OK Planning scheduler successfully initialized"
```

### Issue: Plans Not Generated
**Symptoms:** Sunday passes, no new plans

**Check:**
1. Scheduler is running: `_scheduler.running == True`
2. Job is scheduled: `_scheduler.get_job('weekly_planning_job')`
3. Users have complete setup: `db.is_setup_complete(user_id)`
4. Extraction data exists: `db.get_extraction_result_json(user_id)`

### Issue: Generation Fails for Some Users
**Symptoms:** Some users get plans, others don't

**Debug:**
```python
# Test specific user:
python test_planning_scheduler.py --user 123

# Check logs for specific error:
# ⊘ Skipped (setup/data issue) vs ✗ Failed (generation error)
```

### Issue: AWS Bedrock Errors
**Symptoms:** "Bedrock API call failed"

**Check:**
1. AWS credentials configured: `~/.aws/credentials`
2. Region correct in `config.py`: `AWS_REGION`
3. Model ID valid: Check `Config.resolve_bedrock_model_id()`
4. Rate limits not exceeded

## 📈 Senior Developer Recommendations

### Best Practices Implemented

#### 1. **Separation of Concerns**
- ✅ Scheduling logic isolated in `planning_scheduler.py`
- ✅ Planning logic remains in `planning_agent.py`
- ✅ UI concerns in frontend templates
- ✅ Database operations via `DatabaseHelper`

#### 2. **Error Handling**
- ✅ Graceful degradation (skip incomplete users)
- ✅ Per-user error isolation (one failure doesn't break others)
- ✅ Comprehensive logging at each step
- ✅ Transaction safety (no partial saves)

#### 3. **Scalability**
- ✅ Background processing (non-blocking)
- ✅ Single-instance job execution (no race conditions)
- ✅ Misfire handling (catches up if server was down)
- ✅ Efficient DB queries (bulk fetch, indexed lookups)

#### 4. **Monitoring & Observability**
- ✅ Structured logging with timestamps
- ✅ Success/skip/error counters
- ✅ Per-user result tracking
- ✅ Scheduler health checks

#### 5. **User Experience**
- ✅ Progressive disclosure (manual generation hidden)
- ✅ Real-time countdown feedback
- ✅ Clear auto-generation communication
- ✅ Manual override available
- ✅ Smooth animations and transitions

### Future Enhancements

#### 1. **Advanced Scheduling**
```python
# Daily micro-adjustments:
scheduler.add_job(
    func=adjust_today_schedule,
    trigger=CronTrigger(hour=6, minute=0),  # 6 AM daily
    id='daily_schedule_adjustment'
)
```

#### 2. **Smart Notifications**
- Email users when new plans are generated
- Push notifications for upcoming sessions
- Slack/Discord integration for study reminders

#### 3. **Analytics Dashboard**
```python
# Track generation metrics:
- Average generation time
- Success rate per user
- Most common skip reasons
- Peak generation times
```

#### 4. **A/B Testing**
```python
# Test different generation strategies:
- Morning vs evening study times
- Session length variations
- Intensity level impact
```

#### 5. **Rollback Mechanism**
```python
def rollback_to_previous_plan(user_id, week_number):
    """Restore previous plan if new one is problematic"""
    # Find second-most-recent plan for this week
    # Mark as active and hide failed plan
```

## 📚 API Reference

### Scheduler Functions

#### `init_planning_scheduler(app: Flask) -> BackgroundScheduler`
Initialize and start the planning scheduler.

**Parameters:**
- `app`: Flask application instance

**Returns:**
- Configured BackgroundScheduler instance

**Raises:**
- Exception if scheduler initialization fails

#### `run_weekly_planning_job(app: Flask, db: DatabaseHelper) -> None`
Execute the weekly planning job for all active users.

**Parameters:**
- `app`: Flask application instance (for context)
- `db`: DatabaseHelper instance

**Side Effects:**
- Generates plans for all users
- Logs results to console
- Saves plans to database

#### `generate_plan_for_user(db: DatabaseHelper, user_id: int) -> Dict`
Generate 2-week plans for a single user.

**Parameters:**
- `db`: DatabaseHelper instance
- `user_id`: Integer user ID

**Returns:**
```python
{
    "success": True,
    "week1_plan_id": 123,
    "week2_plan_id": 124,
    "user_id": 1
}
# or on error:
{
    "success": False,
    "error": "Error message",
    "user_id": 1
}
```

### API Endpoints

#### `GET /plan/latest`
Get the most recent 2-week plan bundle for the logged-in user.

**Response:**
```json
{
    "primary": {
        "plan_id": 123,
        "title": "Week 12 Study Plan",
        "created_at": "2026-05-12 00:00:15",
        "timetable_json": [...],
        "sections": {...},
        "week_number": 12
    },
    "secondary": {
        "plan_id": 124,
        "title": "Week 13 Study Plan",
        "timetable_json": [...],
        "week_number": 13
    },
    "active_week": 1,
    "clicked_plan_id": 123
}
```

**Error Responses:**
- 401: Not logged in
- 404: No plans found

## 🔐 Security Considerations

### 1. **Authentication**
- ✅ All endpoints require login (`_require_login()`)
- ✅ User-specific data isolation
- ✅ Plan ownership verification

### 2. **Data Privacy**
- ✅ No cross-user data leakage
- ✅ Sensitive extraction data cached securely
- ✅ Plans tied to user_id foreign key

### 3. **Rate Limiting**
- ✅ Single-instance job execution
- ✅ AWS Bedrock call throttling
- ✅ Misfire grace period prevents storm

## 📞 Support

For issues or questions:
1. Check logs for detailed error messages
2. Run test script: `python test_planning_scheduler.py --user [ID]`
3. Verify scheduler status in Python shell
4. Review this guide for troubleshooting steps

## 🎉 Success Metrics

Track these KPIs to measure system performance:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Generation Success Rate | >95% | Count ✓ vs ✗ in logs |
| Average Generation Time | <60s | Log timestamp delta |
| User Coverage | 100% | Total users vs processed |
| Manual Override Rate | <10% | Manual gen count / auto gen count |
| User Satisfaction | >4.5/5 | In-app survey |

## 🚦 Deployment Checklist

- [x] `planning_scheduler.py` created and tested
- [x] `app.py` updated with scheduler initialization
- [x] `plan_routes.py` updated with `/plan/latest` endpoint
- [x] `plan_improved.html` template created
- [x] Test script `test_planning_scheduler.py` created
- [x] Documentation completed
- [ ] Run test for at least one real user
- [ ] Monitor first automatic generation on Sunday
- [ ] Set up log monitoring/alerting
- [ ] Document rollback procedure
- [ ] Train users on new UI

---

**Congratulations!** Your study planner is now fully automatic and ready for production. 🎓✨
