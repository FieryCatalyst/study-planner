from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import json
import os
from datetime import datetime, timedelta
import io
import base64
import hashlib
import secrets

# Import your existing modules
from data_handler import DataHandler
from scheduler import Scheduler
from progress_tracker import ProgressTracker
from notification import NotificationSystem

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key

# Initialize components
data_handler = DataHandler()
scheduler = Scheduler()
progress_tracker = ProgressTracker(data_handler)
notification_system = NotificationSystem(data_handler)

# Simple user storage (in production, use a proper database)
users_file = os.path.join('data', 'users.json')

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(users_file):
        return {}
    else:
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
                return {}

def save_users(users):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(users_file), exist_ok=True)
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return salt + pwd_hash.hex()

def verify_password(password, hashed):
    """Verify password against hash"""
    salt = hashed[:32]
    stored_hash = hashed[32:]
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return pwd_hash.hex() == stored_hash

@app.route('/')
def login_page():
    """Show login page"""
    return render_template('login.html')

@app.route('/login')
def login_route():
    """Show login page (alternate route)"""
    return render_template('login.html')

@app.route('/app')
def index():
    """Serve the main page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    username = session.get('username', 'User')
    return render_template('index.html', username=username)

@app.route('/guest')
def guest_login():
    """Set up guest session and redirect to app"""
    session['user_id'] = 'guest_user'
    session['username'] = 'Guest'
    session['logged_in'] = True
    session['is_guest'] = True
    return redirect(url_for('index'))

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        users = load_users()
        
        # Check if user already exists
        if username in users or any(u.get('email') == email for u in users.values()):
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        
        # Create new user
        users[username] = {
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat(),
            'plans': []
        }
        
        save_users(users)
        
        # Automatically log in the user after registration
        session['user_id'] = username
        session['username'] = username
        session['logged_in'] = True
        
        return jsonify({'success': True, 'message': 'Registration successful', 'username': username})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        users = load_users()
        
        # Check by username or email
        user = None
        if username in users:
            user = users[username]
            user_key = username
        else:
            for key, u in users.items():
                if u.get('email') == username:
                    user = u
                    user_key = key
                    break
        
        if not user or not verify_password(password, user['password']):
            return jsonify({'success': False, 'error': 'Invalid username/email or password'}), 401
        
        session['user_id'] = user_key
        session['username'] = user_key
        session['logged_in'] = True
        
        return jsonify({'success': True, 'username': user_key})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/create-plan', methods=['POST'])
def create_plan():
    """Create a new study plan"""
    try:
        data = request.json
        subjects = data.get('subjects', [])
        time_available = data.get('time_available_per_day', 4)
        preferred_slots = data.get('preferred_time_slots', [])
        plan_duration = data.get('plan_duration_days', 15)  # New field
        
        # Generate the study plan with duration
        study_plan = scheduler.generate_plan(subjects, time_available, preferred_slots, plan_duration)
        
        # Save the plan
        plan_id = data_handler.save_study_plan(study_plan)
        
        # If user is logged in, associate plan with user
        if session.get('logged_in'):
            users = load_users()
            username = session.get('user_id')
            if username in users:
                if 'plans' not in users[username]:
                    users[username]['plans'] = []
                users[username]['plans'].append(plan_id)
                save_users(users)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'study_plan': study_plan
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-plan/<plan_id>')
def get_plan(plan_id):
    """Get a specific study plan"""
    try:
        plan = data_handler.get_study_plan(plan_id)
        if plan:
            # Add plan_id to the response for frontend use
            plan['plan_id'] = plan_id
            return jsonify({'success': True, 'study_plan': plan})
        else:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-latest-plan')
def get_latest_plan():
    """Get the most recent study plan"""
    try:
        # Get all plans to find the latest one
        all_plans = data_handler._load_plans()
        if not all_plans:
            return jsonify({'success': False, 'error': 'No plans found'}), 404
        
        # Find the most recent plan
        latest_plan_id = max(all_plans.keys(), 
            key=lambda k: all_plans[k].get('created_at', ''))
        plan = all_plans[latest_plan_id]
        plan['plan_id'] = latest_plan_id
        
        return jsonify({'success': True, 'study_plan': plan, 'plan_id': latest_plan_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-all-plans')
def get_all_plans():
    """Get all study plans for the current user"""
    try:
        all_plans = data_handler._load_plans()
        if not all_plans:
            return jsonify({'success': True, 'plans': []})
        
        # Convert to list format with plan_id included
        plans_list = []
        for plan_id, plan_data in all_plans.items():
            plan_summary = {
                'plan_id': plan_id,
                'created_at': plan_data.get('created_at', ''),
                'duration_days': plan_data.get('plan_duration_days', 15),
                'subjects_count': len(plan_data.get('subjects', [])),
                'total_topics': sum(len(subject.get('topics', [])) for subject in plan_data.get('subjects', [])),
                'time_per_day': plan_data.get('time_available_per_day', 4)
            }
            plans_list.append(plan_summary)
        
        # Sort by creation date (newest first)
        plans_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'success': True, 'plans': plans_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-plan/<plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """Delete a specific study plan"""
    try:
        all_plans = data_handler._load_plans()
        
        if plan_id not in all_plans:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
        # Remove the plan
        del all_plans[plan_id]
        
        # Save updated plans
        with open(data_handler.json_path, 'w') as f:
            json.dump(all_plans, f, indent=4)
        
        return jsonify({'success': True, 'message': 'Plan deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update-progress', methods=['POST'])
def update_progress():
    """Update progress for a topic"""
    try:
        data = request.json
        plan_id = data.get('plan_id')
        subject = data.get('subject')
        topic = data.get('topic')
        completed = data.get('completed', False)
        
        success = data_handler.update_progress(plan_id, subject, topic, completed)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to update progress'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress-summary/<plan_id>')
def get_progress_summary(plan_id):
    """Get progress summary for a plan"""
    try:
        summary = progress_tracker.get_progress_summary(plan_id)
        if summary:
            return jsonify({'success': True, 'summary': summary})
        else:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress-chart/<plan_id>')
def get_progress_chart(plan_id):
    """Generate and return progress chart"""
    try:
        # Try to import matplotlib
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
        except ImportError:
            return jsonify({'success': False, 'error': 'Matplotlib not available. Install with: pip install matplotlib'}), 500
        
        summary = progress_tracker.get_progress_summary(plan_id)
        if not summary:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
        # Create the chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('white')
        
        # Overall progress - pie chart
        labels = ['Completed', 'Remaining']
        sizes = [summary['completed_topics'], summary['total_topics'] - summary['completed_topics']]
        colors = ['#48bb78', '#e2e8f0']
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        ax1.set_title('Overall Progress', fontsize=14, fontweight='bold')
        
        # Style the text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # By subject - bar chart
        subjects = list(summary["by_subject"].keys())
        percentages = [data["percentage"] for data in summary["by_subject"].values()]
        
        if subjects:  # Only create bar chart if there are subjects
            bar_colors = ['#667eea' if p < 50 else '#48bb78' for p in percentages]
            bars = ax2.barh(subjects, percentages, color=bar_colors)
            ax2.set_xlim(0, 100)
            ax2.set_xlabel('Completion Percentage', fontweight='bold')
            ax2.set_title('Progress by Subject', fontsize=14, fontweight='bold')
            
            # Add percentage labels to the bars
            for i, (bar, p) in enumerate(zip(bars, percentages)):
                ax2.text(p + 2, i, f"{p}%", va='center', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No subjects found', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Progress by Subject', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return jsonify({
            'success': True,
            'chart': f'data:image/png;base64,{img_base64}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress-chart-timeline/<plan_id>')
def get_progress_chart_timeline(plan_id):
    """Generate and return time-based progress chart"""
    try:
        chart_data = progress_tracker.generate_time_based_chart(plan_id)
        if chart_data:
            return jsonify({
                'success': True,
                'chart': chart_data
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to generate timeline chart'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/historical-progress/<plan_id>')
def get_historical_progress(plan_id):
    """Get historical progress data"""
    try:
        historical_data = progress_tracker.get_historical_progress(plan_id)
        if historical_data:
            return jsonify({'success': True, 'data': historical_data})
        else:
            return jsonify({'success': False, 'error': 'No historical data found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/start', methods=['POST'])
def start_notifications():
    """Start notification service"""
    try:
        data = request.json
        plan_id = data.get('plan_id')
        minutes_before = data.get('minutes_before', 15)
        
        success = notification_system.start_notification_service(plan_id, minutes_before)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/stop', methods=['POST'])
def stop_notifications():
    """Stop notification service"""
    try:
        success = notification_system.stop_notification_service()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/test', methods=['POST'])
def test_notification():
    """Send a test notification"""
    try:
        available = notification_system.send_test_notification()
        return jsonify({'success': True, 'notifications_available': available})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user-status')
def user_status():
    """Get current user status"""
    return jsonify({
        'logged_in': 'user_id' in session,
        'username': session.get('username')
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Check if running in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
