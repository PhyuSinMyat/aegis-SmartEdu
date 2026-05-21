# Quick Start Guide - Automatic Study Planner

## 🚀 Getting Started in 5 Minutes

### Step 1: Verify Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test the Scheduler
```bash
# Test with one user:
python test_planning_scheduler.py --user 1

# Test with all users:
python test_planning_scheduler.py
```

### Step 3: Start the App
```bash
python app.py
```

Look for these log messages:
```
[AppInit] OK Summary scheduler successfully initialized
[AppInit] OK Planning scheduler successfully initialized
Planning scheduler started successfully
  - Job: Weekly Study Plan Generation
  - Schedule: Every Sunday at 12:00 AM
  - Next run: 2026-05-18 00:00:00
```

### Step 4: View the Dashboard
1. Navigate to `http://localhost:5000/plan`
2. You should see the auto-generation banner
3. Countdown shows time until next Sunday

---

## 📊 What Happens Every Sunday at Midnight?

```
00:00:00 → Scheduler triggers weekly job
00:00:01 → Fetch all active user IDs from database
00:00:02 → For each user:
            ├─ Check if setup complete
            ├─ Load extraction data
            ├─ Generate Week N plan (~30-45s)
            ├─ Save to database
            ├─ Generate Week N+1 plan (~30-45s)
            └─ Save to database
00:15:00 → Job complete (for 100 users)
```

---

## 🧪 Testing Checklist

- [ ] Test single user generation: `python test_planning_scheduler.py --user 1`
- [ ] Verify plan saved in database
- [ ] Check `/plan/latest` API endpoint returns data
- [ ] View dashboard, confirm auto-generation banner displays
- [ ] Verify countdown timer updates
- [ ] Test manual generation still works
- [ ] Check logs for any errors

---

## 📁 Files Added/Modified

### New Files:
- `backend/services/planning_scheduler.py` - Scheduling logic
- `frontend/templates/plan_improved.html` - Enhanced UI
- `test_planning_scheduler.py` - Test script
- `AUTOMATIC_PLANNING_GUIDE.md` - Full documentation
- `SENIOR_DEVELOPER_RECOMMENDATIONS.md` - Architecture guide
- `QUICKSTART.md` - This file

### Modified Files:
- `app.py` - Added scheduler initialization
- `backend/routes/plan_routes.py` - Added `/plan/latest` endpoint

---

## 🔧 Quick Configuration

### Change Schedule Time
Edit `backend/services/planning_scheduler.py` line 250:

```python
scheduler.add_job(
    trigger=CronTrigger(
        day_of_week='sun',  # mon, tue, wed, thu, fri, sat, sun
        hour=0,             # 0-23
        minute=0,           # 0-59
    ),
    # ...
)
```

### Disable Auto-Generation (for testing)
Comment out in `app.py` around line 175:

```python
# init_planning_scheduler(app)
```

---

## 🐛 Common Issues

### "No module named 'planning_scheduler'"
**Solution:** Make sure you're in the project root directory

### "Scheduler not running"
**Solution:** Check if `WERKZEUG_RUN_MAIN` is `true`:
```bash
export WERKZEUG_RUN_MAIN=true  # Linux/Mac
set WERKZEUG_RUN_MAIN=true     # Windows
```

### "Plans not generating automatically"
**Solution:**
1. Check scheduler status in logs
2. Verify next run time is correct
3. Ensure users have complete setup

---

## 📞 Need Help?

1. Check `AUTOMATIC_PLANNING_GUIDE.md` for detailed documentation
2. Review `SENIOR_DEVELOPER_RECOMMENDATIONS.md` for architecture
3. Check logs for specific error messages
4. Test with: `python test_planning_scheduler.py --user [ID]`

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ Logs show "Planning scheduler successfully initialized"
- ✅ `/plan/latest` endpoint returns 2-week plan data
- ✅ Dashboard displays auto-generation banner
- ✅ Countdown timer shows time to Sunday
- ✅ Test script generates plans without errors

---

**Congratulations! Your automatic study planner is ready!** 🎉
