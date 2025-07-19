import random
from datetime import datetime, timedelta

class Scheduler:
    def __init__(self):
        """Initialize the scheduler"""
        pass
    
    def generate_plan(self, subjects, time_available_per_day, preferred_time_slots=None, plan_duration_days=15):
        """
        Generate a study plan based on subjects, time available, and preferences
        
        Parameters:
        - subjects: List of dictionaries with subject details
        - time_available_per_day: Hours available per day
        - preferred_time_slots: Optional preferred study times
        - plan_duration_days: Number of days for the plan (7, 15, 30, 60)
        
        Returns: A complete study plan
        """
        total_weight = sum(subject['weight'] for subject in subjects)
        
        # Calculate time allocation for each subject based on weight
        for subject in subjects:
            weight_ratio = subject['weight'] / total_weight
            subject['allocated_hours'] = round(time_available_per_day * weight_ratio, 1)
            
            # Ensure topics have IDs for tracking
            for i, topic in enumerate(subject['topics']):
                if 'id' not in topic:
                    topic['id'] = f"{subject['name']}-topic-{i+1}"
                topic['completed'] = False
        
        # Create daily schedule for specified duration
        schedule = self._create_daily_schedule(subjects, preferred_time_slots, plan_duration_days)
        
        study_plan = {
            "subjects": subjects,
            "time_available_per_day": time_available_per_day,
            "plan_duration_days": plan_duration_days,
            "daily_schedule": schedule,
            "progress": {
                "completed_topics": 0,
                "total_topics": sum(len(subject['topics']) for subject in subjects)
            }
        }
        
        return study_plan
    
    def _create_daily_schedule(self, subjects, preferred_time_slots=None, plan_duration_days=15):
        """Create a daily schedule for the specified number of days"""
        daily_schedule = {}
        today = datetime.now()
        
        # Default time slots if none provided
        if not preferred_time_slots:
            preferred_time_slots = ["08:00-10:00", "14:00-16:00", "19:00-21:00"]
        
        # Create schedule for specified number of days
        for i in range(plan_duration_days):
            day = today + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            daily_schedule[day_str] = []
            
            # Distribute subjects across time slots
            slot_index = 0
            for subject in subjects:
                # Skip if no topics in this subject
                if not subject['topics']:
                    continue
                
                # Add subject to this day's schedule
                if slot_index < len(preferred_time_slots):
                    # Find topics not yet scheduled
                    unscheduled_topics = [
                        topic for topic in subject['topics'] 
                        if not any(
                            scheduled_item.get('topic_id') == topic['id']
                            for day_items in daily_schedule.values()
                            for scheduled_item in day_items
                        )
                    ]
                    
                    if unscheduled_topics:
                        topic = unscheduled_topics[0]
                        daily_schedule[day_str].append({
                            "subject": subject['name'],
                            "topic": topic['name'],
                            "topic_id": topic['id'],
                            "time_slot": preferred_time_slots[slot_index],
                            "duration": "2 hours",
                            "priority": self._calculate_priority(topic)
                        })
                        slot_index += 1
            
            # If we have more time slots than subjects, add more topics
            if slot_index < len(preferred_time_slots):
                for subject in subjects:
                    if slot_index >= len(preferred_time_slots):
                        break
                    
                    # Find more topics to fill remaining slots
                    more_topics = [
                        topic for topic in subject['topics']
                        if not any(
                            scheduled_item.get('topic_id') == topic['id']
                            for day_items in daily_schedule.values()
                            for scheduled_item in day_items
                        )
                    ]
                    
                    if more_topics:
                        topic = more_topics[0]
                        daily_schedule[day_str].append({
                            "subject": subject['name'],
                            "topic": topic['name'],
                            "topic_id": topic['id'],
                            "time_slot": preferred_time_slots[slot_index],
                            "duration": "2 hours",
                            "priority": self._calculate_priority(topic)
                        })
                        slot_index += 1
        
        return daily_schedule
    
    def _calculate_priority(self, topic):
        """Calculate priority based on difficulty and deadline"""
        # Default priority is medium
        priority = 2
        
        # Adjust based on difficulty
        if 'difficulty' in topic:
            if topic['difficulty'] == 'high':
                priority += 1
            elif topic['difficulty'] == 'low':
                priority -= 1
        
        # Adjust based on deadline if present
        if 'deadline' in topic:
            deadline = datetime.strptime(topic['deadline'], "%Y-%m-%d")
            days_left = (deadline - datetime.now()).days
            
            if days_left <= 3:
                priority += 2
            elif days_left <= 7:
                priority += 1
        
        # Ensure priority is between 1-5
        return max(1, min(5, priority))
    
    def adjust_plan(self, study_plan, completed_topics):
        """Adjust the plan based on completed topics"""
        # Update completed status
        for topic_id in completed_topics:
            for subject in study_plan['subjects']:
                for topic in subject['topics']:
                    if topic['id'] == topic_id:
                        topic['completed'] = True
        
        # Update progress
        completed_count = sum(
            sum(1 for topic in subject['topics'] if topic.get('completed', False))
            for subject in study_plan['subjects']
        )
        
        study_plan['progress']['completed_topics'] = completed_count
        
        # Regenerate schedule if needed
        if completed_count > 0:
            study_plan['daily_schedule'] = self._create_daily_schedule(
                study_plan['subjects']
            )
        
        return study_plan