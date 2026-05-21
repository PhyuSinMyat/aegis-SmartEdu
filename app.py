import atexit
import os
import sqlite3
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import psutil

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from backend.routes.upload_routes import upload_bp
from backend.routes.plan_routes import plan_bp
from backend.routes.summary_routes import summary_bp
from backend.routes.tracker_routes import tracker_bp
from backend.routes.coach_routes import coach_bp
from backend.routes.assignment_checker_routes import assignment_checker_bp
from backend.services.summary_scheduler import init_scheduler
from backend.services.planning_scheduler import init_planning_scheduler, shutdown_planning_scheduler
from backend.utils.template_context import build_user_page_context
from config import Config
from database import DatabaseHelper
from form import CreateUserForm, LoginForm

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'frontend' / 'templates'
STATIC_DIR = BASE_DIR / 'frontend' / 'static'
UPLOAD_DIR = BASE_DIR / 'uploads' / 'timetables'
PROFILE_PIC_DIR = STATIC_DIR / 'profile_pics'
ALLOWED_PROFILE_PIC_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

TRAY_SCRIPT = BASE_DIR / 'smartedu_tray.py'
_tray_process: subprocess.Popen | None = None

def _stop_existing_trays() -> None:
    current_pid = os.getpid()
    tray_processes: list[psutil.Process] = []

    for proc in psutil.process_iter(["pid", "cmdline"]):
        try:
            if proc.info["pid"] == current_pid:
                continue
            cmdline = " ".join(proc.info["cmdline"] or [])
            if "smartedu_tray.py" in cmdline:
                tray_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    for proc in tray_processes:
        try:
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    _, alive = psutil.wait_procs(tray_processes, timeout=5)
    for proc in alive:
        try:
            proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def _launch_tray() -> None:
    global _tray_process
    if not TRAY_SCRIPT.exists():
        return
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return

    try:
        _stop_existing_trays()
    except Exception as exc:
        print(f"[Tray] Could not stop existing tray process: {exc}")

    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")
    runner = str(pythonw) if pythonw.exists() else str(exe)

    try:
        _tray_process = subprocess.Popen(
            [runner, str(TRAY_SCRIPT), "--parent-pid", str(os.getpid())],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except OSError as exc:
        _tray_process = None
        print(f"[Tray] Could not launch SmartEdu tray tracker: {exc}")

def _stop_launched_tray() -> None:
    global _tray_process
    proc = _tray_process
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        try:
            proc.kill()
        except OSError:
            pass
    finally:
        _tray_process = None

atexit.register(_stop_launched_tray)


def create_app():
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
    app.secret_key = Config.SECRET_KEY
    app.permanent_session_lifetime = timedelta(days=7)
    app.config['SESSION_COOKIE_SECURE']   = Config.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY

    app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_PIC_DIR.mkdir(parents=True, exist_ok=True)

    @app.after_request
    def allow_extension_origin(response):
        origin = request.headers.get('Origin', '')
        if origin.startswith('chrome-extension://') or origin.startswith('moz-extension://'):
            response.headers['Access-Control-Allow-Origin']      = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers']     = 'Content-Type'
            response.headers['Access-Control-Allow-Methods']     = 'GET, POST, OPTIONS'
        return response

    @app.route('/tracker/heartbeat', methods=['OPTIONS'])
    @app.route('/tracker/status', methods=['OPTIONS'])
    def handle_preflight():
        return '', 204

    db = DatabaseHelper()
    app.register_blueprint(upload_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(tracker_bp)
    app.register_blueprint(coach_bp)
    app.register_blueprint(assignment_checker_bp)


    @app.context_processor
    def inject_current_user():
        user_id = session.get('user_id')
        current_user = db.get_user_by_id(user_id) if user_id else None
        avatar_url = None
        if current_user and current_user.get_profile_pic():
            avatar_url = url_for('static', filename=current_user.get_profile_pic())
        return {
            'current_user': current_user,
            'current_user_initials': (
                (current_user.get_username()[:2] if current_user else 'U').upper()
            ),
            'current_user_avatar_url': avatar_url,
        }
    
    # Initialize the background scheduler for daily summaries
    # Only start in the main process (not in Flask debug reloader)
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("[AppInit] Running in reloader process – schedulers will be started in main process")
    else:
        print("[AppInit] Starting schedulers in main Flask process")
        try:
            # Initialize daily summary scheduler (existing)
            init_scheduler(app, db)
            print("[AppInit] OK Summary scheduler successfully initialized")

            # Initialize weekly planning scheduler (new)
            init_planning_scheduler(app)
            print("[AppInit] OK Planning scheduler successfully initialized")
        except Exception as exc:
            print(f"[AppInit] FAIL Failed to initialize schedulers: {exc}")
            raise

        # Register shutdown handler for planning scheduler
        atexit.register(shutdown_planning_scheduler)

    def require_login():
        user_id = session.get('user_id')
        if user_id is None:
            flash('Please log in first.', 'danger')
            return None
        return user_id

    @app.route('/')
    def home():
        return redirect(url_for('welcome'))

    @app.route('/welcome')
    def welcome():
        return render_template('welcome.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            user = db.get_user_by_identifier((form.identifier.data or '').strip().lower())
            if not user or not check_password_hash(user.get_password_hash(), form.password.data):
                flash('Incorrect login details.', 'danger')
                return render_template('login.html', form=form)
            session['user_id'] = user.get_user_id()
            session['username'] = user.get_username()
            session.permanent = bool(form.remember_me.data)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('reflection'))
        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = CreateUserForm(request.form)
        if request.method == 'POST' and form.validate():
            username = (form.username.data or '').strip().lower()
            email = (form.email.data or '').strip().lower()
            if db.get_user_by_username(username):
                form.username.errors.append('Username already taken.')
                return render_template('register.html', form=form)
            if db.get_user_by_identifier(email):
                form.email.errors.append('Email already registered.')
                return render_template('register.html', form=form)

            profile_pic_rel_path = ''
            saved_profile_pic_path = None
            profile_pic_file = request.files.get('profile_pic')
            if profile_pic_file and profile_pic_file.filename:
                file_extension = Path(profile_pic_file.filename).suffix.lower().lstrip('.')
                if file_extension not in ALLOWED_PROFILE_PIC_EXTENSIONS:
                    flash('Profile picture must be a PNG, JPG, JPEG, GIF, or WEBP image.', 'danger')
                    return render_template('register.html', form=form)

                safe_name = secure_filename(profile_pic_file.filename)
                unique_name = f"user_new_{uuid4().hex[:8]}_{safe_name}"
                save_path = PROFILE_PIC_DIR / unique_name
                profile_pic_file.save(save_path)
                saved_profile_pic_path = save_path
                profile_pic_rel_path = f"profile_pics/{unique_name}"

            try:
                user_id = db.insert_user(
                    username,
                    email,
                    generate_password_hash(form.password.data),
                    profile_pic=profile_pic_rel_path,
                )
            except sqlite3.IntegrityError:
                if saved_profile_pic_path and saved_profile_pic_path.exists():
                    try:
                        saved_profile_pic_path.unlink()
                    except OSError:
                        app.logger.warning("Could not remove profile picture after registration failure: %s", saved_profile_pic_path)
                form.username.errors.append('Username or email already registered.')
                return render_template('register.html', form=form)
            session['user_id'] = user_id
            session['username'] = username
            session.permanent = True
            flash('Account created. Please upload your timetable files.', 'success')
            return redirect(url_for('upload.upload'))
        return render_template('register.html', form=form)

    @app.route('/reflection')
    def reflection():
        user_id = require_login()
        if user_id is None:
            return redirect(url_for('login'))

        # Fetch only the weeks that have saved study plans in the database
        from backend.routes.plan_routes import _build_latest_saved_plan_history
        from backend.agents.planning_agent import compute_academic_week
        raw_plans = db.get_study_plans_by_user_id(user_id) or []
        history = _build_latest_saved_plan_history(raw_plans)
        available_weeks = sorted(
            [item['week_number'] for item in history if item.get('week_number') is not None]
        )

        # Determine which week to show: prefer current week if it exists in available_weeks, else last week
        display_week = None
        if available_weeks:
            # Get user's semester start date to calculate current week
            preferences = db.get_study_preferences_by_user_id(user_id)
            if preferences and preferences.get('semester_start_date'):
                from datetime import date
                current_week_number = compute_academic_week(preferences['semester_start_date'], date.today().isoformat())
                # If current week has a saved plan, use it; otherwise fall back to last available week
                if current_week_number in available_weeks:
                    display_week = current_week_number
                else:
                    display_week = available_weeks[-1]
            else:
                # No semester start date, default to last available week
                display_week = available_weeks[-1]

        # Pre-compute real stats for the display week so the page renders with live data
        initial_stats = None
        initial_daily_hours = []
        initial_module_stats = []
        initial_study_patterns = None
        initial_performance_highlights = None
        if display_week is not None:
            initial_stats = db.get_reflection_week_stats(user_id, display_week)
            initial_daily_hours = db.get_daily_hours_for_week(user_id, display_week)
            initial_module_stats = db.get_reflection_module_stats(user_id, display_week)
            initial_study_patterns = db.get_reflection_study_patterns(user_id, display_week)
            initial_performance_highlights = db.get_reflection_performance_highlights(user_id, display_week)

            # Debug: print what we got
            print(f"[DEBUG] Performance highlights for week {display_week}: {initial_performance_highlights}")

        # Get upcoming deadlines from extraction cache
        upcoming_deadlines = db.get_upcoming_deadlines(user_id, limit=3)

        return render_template(
            'reflection.html',
            current_page='reflection',
            available_weeks=available_weeks,
            display_week=display_week,
            initial_stats=initial_stats,
            initial_daily_hours=initial_daily_hours,
            initial_module_stats=initial_module_stats,
            initial_study_patterns=initial_study_patterns,
            initial_performance_highlights=initial_performance_highlights,
            upcoming_deadlines=upcoming_deadlines,
            **build_user_page_context(db, user_id)
        )

    @app.route('/api/reflection/available-weeks')
    def get_reflection_available_weeks():
        user_id = require_login()
        if user_id is None:
            return jsonify({'error': 'Authentication required'}), 401

        from backend.routes.plan_routes import _build_latest_saved_plan_history
        raw_plans = db.get_study_plans_by_user_id(user_id) or []
        history = _build_latest_saved_plan_history(raw_plans)
        available_weeks = sorted(
            [item['week_number'] for item in history if item.get('week_number') is not None]
        )
        return jsonify({'available_weeks': available_weeks})

    @app.route('/api/reflection/week/<int:week_number>')
    def get_reflection_week_data(week_number):
        user_id = require_login()
        if user_id is None:
            return jsonify({'error': 'Authentication required'}), 401

        # Validate that this week actually exists in the saved study plans
        from backend.routes.plan_routes import _build_latest_saved_plan_history
        raw_plans = db.get_study_plans_by_user_id(user_id) or []
        history = _build_latest_saved_plan_history(raw_plans)
        available_weeks = [item['week_number'] for item in history if item.get('week_number') is not None]

        if week_number not in available_weeks:
            return jsonify({'error': f'Week {week_number} has no saved study plan'}), 404

        # Fetch real stats from the database
        stats = db.get_reflection_week_stats(user_id, week_number)
        daily_hours = db.get_daily_hours_for_week(user_id, week_number)
        module_stats = db.get_reflection_module_stats(user_id, week_number)
        study_patterns = db.get_reflection_study_patterns(user_id, week_number)
        performance_highlights = db.get_reflection_performance_highlights(user_id, week_number)
        return jsonify({
            'week_number': week_number,
            'stats': stats,
            'daily_hours': daily_hours,
            'module_stats': module_stats,
            'study_patterns': study_patterns,
            'performance_highlights': performance_highlights,
        })

    @app.route('/api/debug/quiz-results')
    def debug_quiz_results():
        """Debug endpoint to check if quiz results are being saved"""
        user_id = require_login()
        if user_id is None:
            return jsonify({'error': 'Authentication required'}), 401

        # Get all quiz results for this user
        with db._get_connection() as conn:
            results = conn.execute(
                '''
                SELECT q.*, s.subject, s.summary_date, s.topic
                FROM quiz_results q
                JOIN daily_summary_cards s ON q.summary_id = s.summary_id
                WHERE q.user_id = ?
                ORDER BY q.created_at DESC
                LIMIT 20
                ''',
                (user_id,)
            ).fetchall()

        return jsonify({
            'count': len(results),
            'results': [dict(r) for r in results]
        })

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        user_id = require_login()
        if user_id is None:
            return redirect(url_for('login'))
        if request.method == 'POST':
            current_user = db.get_user_by_id(user_id)
            if current_user is None:
                flash('Could not load your account details.', 'danger')
                return redirect(url_for('profile'))

            new_username = (request.form.get('username') or '').strip().lower()
            if not new_username:
                flash('Username cannot be empty.', 'danger')
                return redirect(url_for('profile'))
            if len(new_username) < 3:
                flash('Username must be at least 3 characters long.', 'danger')
                return redirect(url_for('profile'))

            existing_user = db.get_user_by_username(new_username)
            if existing_user and existing_user.get_user_id() != user_id:
                flash('That username is already taken.', 'danger')
                return redirect(url_for('profile'))

            profile_pic_rel_path = current_user.get_profile_pic()
            profile_pic_file = request.files.get('profile_pic')
            if profile_pic_file and profile_pic_file.filename:
                file_extension = Path(profile_pic_file.filename).suffix.lower().lstrip('.')
                if file_extension not in ALLOWED_PROFILE_PIC_EXTENSIONS:
                    flash('Profile picture must be a PNG, JPG, JPEG, GIF, or WEBP image.', 'danger')
                    return redirect(url_for('profile'))

                safe_name = secure_filename(profile_pic_file.filename)
                unique_name = f"user_{user_id}_{uuid4().hex[:8]}_{safe_name}"
                save_path = PROFILE_PIC_DIR / unique_name
                profile_pic_file.save(save_path)
                profile_pic_rel_path = f"profile_pics/{unique_name}"

                old_profile_pic = current_user.get_profile_pic()
                if old_profile_pic:
                    old_path = STATIC_DIR / old_profile_pic
                    if old_path.exists() and old_path.is_file():
                        try:
                            old_path.unlink()
                        except OSError:
                            app.logger.warning("Could not remove previous profile picture: %s", old_path)

            db.update_user_profile(user_id, new_username, profile_pic_rel_path)
            session['username'] = new_username
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))

        return render_template('profile.html', current_page='profile', hide_sidebar=True, **build_user_page_context(db, user_id))

    @app.route('/settings')
    def settings():
        user_id = require_login()
        if user_id is None:
            return redirect(url_for('login'))
        return redirect(url_for('profile'))

    @app.route('/delete-account', methods=['POST'])
    def delete_account():
        user_id = require_login()
        if user_id is None:
            return redirect(url_for('login'))

        current_user = db.get_user_by_id(user_id)
        if current_user is None:
            session.clear()
            flash('Account not found. Please log in again.', 'warning')
            return redirect(url_for('login'))

        # Delete uploaded timetable files from disk.
        for item in db.get_uploaded_files_by_user_id(user_id):
            raw_path = (item.get('file_path') or '').strip()
            if not raw_path:
                continue
            try:
                file_path = Path(raw_path)
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
            except OSError:
                app.logger.warning('Could not delete uploaded file during account deletion: %s', raw_path)

        # Remove per-user upload directory if empty.
        try:
            user_upload_dir = UPLOAD_DIR / f'user_{user_id}'
            if user_upload_dir.exists() and user_upload_dir.is_dir():
                for leftover in user_upload_dir.iterdir():
                    if leftover.is_file():
                        leftover.unlink()
                user_upload_dir.rmdir()
        except OSError:
            app.logger.warning('Could not fully remove upload directory for user %s', user_id)

        # Delete profile picture file from disk.
        profile_pic_rel_path = current_user.get_profile_pic()
        if profile_pic_rel_path:
            try:
                profile_pic_path = STATIC_DIR / profile_pic_rel_path
                if profile_pic_path.exists() and profile_pic_path.is_file():
                    profile_pic_path.unlink()
            except OSError:
                app.logger.warning('Could not delete profile picture during account deletion: %s', profile_pic_rel_path)

        db.delete_user_and_related_data(user_id)
        session.clear()
        flash('Your account and all related data were deleted successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'success')
        return redirect(url_for('login'))

    return app


app = create_app()

if __name__ == '__main__':
    _launch_tray()
    app.run(debug=True)
