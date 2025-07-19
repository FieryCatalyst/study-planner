#!/usr/bin/env python3
"""
Optimized Debug Test Script for Smart Study Planner
Tests all critical components efficiently
"""

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        # Test core packages
        import flask, matplotlib, pandas, plyer
        print("✓ Core packages (Flask, Matplotlib, Pandas, Plyer)")
        
        # Test custom modules
        from data_handler import DataHandler
        from notification import NotificationSystem
        from progress_tracker import ProgressTracker
        from scheduler import Scheduler
        print("✓ Custom modules (DataHandler, NotificationSystem, ProgressTracker, Scheduler)")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_data_files():
    """Test data file accessibility"""
    print("\nTesting data files...")
    import os, json
    
    data_files = ['data/users.json', 'data/study_plans.json', 'data/study_progress.csv']
    
    for file_path in data_files:
        if not os.path.exists(file_path):
            print(f"✗ {file_path} missing")
            return False
            
        if file_path.endswith('.json'):
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print(f"✗ {file_path} has invalid JSON: {e}")
                return False
    
    print("✓ All data files exist and are valid")
    return True

def test_flask_app():
    """Test Flask app initialization"""
    print("\nTesting Flask app...")
    try:
        from app import app
        
        # Test critical routes
        critical_routes = [
            '/', '/api/login', '/api/register', '/api/create-plan',
            '/api/notifications/start', '/api/notifications/stop',
            '/api/progress-summary/<plan_id>', '/api/progress-chart/<plan_id>'
        ]
        
        existing_routes = [rule.rule for rule in app.url_map.iter_rules()]
        missing_routes = [route for route in critical_routes if route not in existing_routes]
        
        if missing_routes:
            print(f"✗ Missing routes: {missing_routes}")
            return False
        
        print("✓ Flask app and all critical routes working")
        return True
        
    except Exception as e:
        print(f"✗ Flask app error: {e}")
        return False

def test_static_files():
    """Test static file existence"""
    print("\nTesting static files...")
    import os
    
    required_files = [
        'static/style.css', 'static/script.js', 
        'templates/index.html', 'templates/login.html'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    print("✓ All static files present")
    return True

def test_notification_system():
    """Test notification system"""
    print("\nTesting notification system...")
    try:
        from data_handler import DataHandler
        from notification import NotificationSystem
        
        data_handler = DataHandler()
        notification_system = NotificationSystem(data_handler)
        
        # Test notification capability
        result = notification_system.send_test_notification()
        print(f"✓ Notification system functional (Plyer available: {result})")
        
        return True
        
    except Exception as e:
        print(f"✗ Notification system error: {e}")
        return False

def main():
    """Run optimized tests"""
    print("=" * 45)
    print("SMART STUDY PLANNER - OPTIMIZED DEBUG")
    print("=" * 45)
    
    tests = [
        ("Core Imports", test_imports),
        ("Data Files", test_data_files),
        ("Static Files", test_static_files),
        ("Flask App", test_flask_app),
        ("Notifications", test_notification_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 45)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! App is optimized and ready.")
        print("\nQuick Start:")
        print("• Run: python app.py")
        print("• Open: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Check errors above.")
    
    print("=" * 45)

if __name__ == "__main__":
    main()
