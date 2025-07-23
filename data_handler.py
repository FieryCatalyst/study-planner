import json
import os
import csv
from datetime import datetime

class DataHandler:
    def __init__(self, data_dir="data"):
        """Initialize data handler with directory for storing data"""
        self.data_dir = data_dir
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.json_path = os.path.join(data_dir, "study_plans.json")
        self.csv_path = os.path.join(data_dir, "study_progress.csv")
    
    def save_study_plan(self, study_plan):
        """Save the study plan to a JSON file"""
        # Load existing plans if any
        all_plans = self._load_plans()
        
        # Add timestamp to the new plan
        study_plan['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate a unique ID for the plan (timestamp-based)
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        all_plans[plan_id] = study_plan
        
        # Save all plans
        with open(self.json_path, 'w') as f:
            json.dump(all_plans, f, indent=4)
        
        return plan_id
    
    def _load_plans(self):
        """Load all study plans from JSON file"""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Return empty dict if JSON is invalid
                return {}
        return {}
    
    def get_study_plan(self, plan_id=None):
        """Get a specific study plan or the most recent one"""
        all_plans = self._load_plans()
        
        if not all_plans:
            return None
            
        if plan_id is None:
            # Return the most recent plan if no ID specified
            latest_plan_id = max(all_plans.keys(), 
                key=lambda k: all_plans[k].get('created_at', ''))
            return all_plans[latest_plan_id]
        
        return all_plans.get(plan_id)
    
    def update_progress(self, plan_id, subject, topic, completed):
        """Update progress for a specific topic"""
        all_plans = self._load_plans()
        
        if plan_id not in all_plans:
            return False
            
        # Find the topic in the plan and update completion status this-> O(n*2)->o(s+t) now this is linear 
        for subj in all_plans[plan_id]['subjects']:  
            if subj['name'] != subject:
                continue
            for topic_obj in subj['topics']:         
                if topic_obj['name'] == topic:
                    topic_obj['completed'] = completed
                    topic_obj['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else None
                break
            break

        
        # Save the updated plans
        with open(self.json_path, 'w') as f:
            json.dump(all_plans, f, indent=4)
            
        # Also log progress in CSV for analysis
        self._log_progress(plan_id, subject, topic, completed)
        
        return True
    
    def _log_progress(self, plan_id, subject, topic, completed):
        """Log progress in CSV file for historical tracking"""
        header = ['timestamp', 'plan_id', 'subject', 'topic', 'completed']
        file_exists = os.path.exists(self.csv_path)
        
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                plan_id,
                subject,
                topic,
                "Yes" if completed else "No"
            ])