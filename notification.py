from datetime import datetime, timedelta
import time
import threading
    
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

class NotificationSystem:
    def __init__(self, data_handler):
        """Initialize the notification system with data handler"""
        self.data_handler = data_handler
        self.notification_thread = None
        self.stop_notifications = threading.Event()
    
    def start_notification_service(self, plan_id=None, minutes_before=15):
        """Start a background thread to check and send notifications"""
        if not NOTIFICATIONS_AVAILABLE:
            print("Warning: plyer package not found. Notifications are disabled.")
            return False
        
        if self.notification_thread and self.notification_thread.is_alive():
            # Already running
            return True
        
        self.stop_notifications.clear()
        self.notification_thread = threading.Thread(
            target=self._notification_loop,
            args=(plan_id, minutes_before),
            daemon=True
        )
        self.notification_thread.start()
        return True
    
    def stop_notification_service(self):
        """Stop the notification service"""
        if self.notification_thread and self.notification_thread.is_alive():
            self.stop_notifications.set()
            self.notification_thread.join(timeout=1.0)
            return True
        return False
    
    def _notification_loop(self, plan_id, minutes_before):
        """Background loop to check and send notifications"""
        while not self.stop_notifications.is_set():
            try:
                # Get current plan
                plan = self.data_handler.get_study_plan(plan_id)
                if not plan:
                    time.sleep(60)  # Sleep for a minute and try again
                    continue
                
                # Get today's date
                today = datetime.now().strftime("%Y-%m-%d")
                
                # Check if we have schedule for today
                if today in plan['daily_schedule']:
                    
                    for item in plan['daily_schedule'][today]:
                        # Check if this item has a time slot coming up
                        time_slot = item['time_slot']
                        if '-' in time_slot:
                            start_time_str = time_slot.split('-')[0].strip()
                            try:
                                # Parse the time
                                hour, minute = map(int, start_time_str.split(':'))
                                start_time = datetime.now().replace(
                                    hour=hour, minute=minute, second=0, microsecond=0
                                )
                                
                                # Calculate time until this slot
                                now = datetime.now()
                                time_delta = start_time - now
                                
                                # If it's within the notification window and in the future
                                if 0 < time_delta.total_seconds() <= minutes_before * 60:
                                    self._send_notification(
                                        f"Study Reminder: {item['subject']}",
                                        f"Time to study {item['topic']} in {minutes_before} minutes!"
                                    )
                            except (ValueError, AttributeError):
                                pass  # Skip if time format is invalid
                
                # Sleep for a minute before checking again
                for _ in range(60):  # Check every second if we should stop
                    if self.stop_notifications.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error in notification thread: {e}")
                time.sleep(60)  # Sleep and retry
    
    def _send_notification(self, title, message):
        """Send a desktop notification"""
        if NOTIFICATIONS_AVAILABLE:
            notification.notify(
                title=title,
                message=message,
                app_name="Smart Study Planner",
                timeout=10
            )
        else:
            # Fallback to printing
            print(f"\n[NOTIFICATION] {title}: {message}\n")
    
    def send_test_notification(self):
        """Send a test notification to verify it works"""
        self._send_notification(
            "Smart Study Planner",
            "This is a test notification. If you see this, notifications are working!"
        )
        return NOTIFICATIONS_AVAILABLE