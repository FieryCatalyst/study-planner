import matplotlib.pyplot as plt
import os
import pandas as pd
from datetime import datetime, timedelta

class ProgressTracker:
    def __init__(self, data_handler):
        """Initialize the progress tracker with data handler"""
        self.data_handler = data_handler
    
    def get_progress_summary(self, plan_id=None):
        """Get a summary of progress for a specific plan"""
        study_plan = self.data_handler.get_study_plan(plan_id)
        
        if not study_plan:
            return None
        
        summary = {
            "total_subjects": len(study_plan["subjects"]),
            "total_topics": sum(len(subject["topics"]) for subject in study_plan["subjects"]),
            "completed_topics": 0,
            "completion_percentage": 0,
            "by_subject": {}
        }
        
        # Calculate completed topics and percentage
        for subject in study_plan["subjects"]:
            completed_in_subject = sum(1 for topic in subject["topics"] if topic.get("completed", False))
            total_in_subject = len(subject["topics"])
            
            summary["by_subject"][subject["name"]] = {
                "total": total_in_subject,
                "completed": completed_in_subject,
                "percentage": round((completed_in_subject / total_in_subject * 100) if total_in_subject > 0 else 0, 1)
            }
            
            summary["completed_topics"] += completed_in_subject
        
        if summary["total_topics"] > 0:
            summary["completion_percentage"] = round(summary["completed_topics"] / summary["total_topics"] * 100, 1)
        
        return summary
    
    def visualize_progress_ascii(self, plan_id=None):
        """Generate ASCII chart of progress"""
        summary = self.get_progress_summary(plan_id)
        
        if not summary:
            return "No study plan found."
        
        output = []
        output.append("=== Study Progress ===")
        output.append(f"Overall: {summary['completion_percentage']}% complete")
        output.append(f"[{'#' * int(summary['completion_percentage'] / 10)}{' ' * (10 - int(summary['completion_percentage'] / 10))}]")
        output.append(f"{summary['completed_topics']}/{summary['total_topics']} topics completed\n")
        
        output.append("--- By Subject ---")
        for subject, data in summary["by_subject"].items():
            bar_length = int(data["percentage"] / 10)
            output.append(f"{subject}: {data['percentage']}%")
            output.append(f"[{'#' * bar_length}{' ' * (10 - bar_length)}] {data['completed']}/{data['total']}")
        
        return "\n".join(output)
    
    def visualize_progress_matplotlib(self, plan_id=None, save_path=None):
        """Generate matplotlib chart of progress"""
        summary = self.get_progress_summary(plan_id)
        
        if not summary:
            return False
        
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Overall progress - pie chart
        labels = ['Completed', 'Remaining']
        sizes = [summary['completed_topics'], summary['total_topics'] - summary['completed_topics']]
        colors = ['#4CAF50', '#F5F5F5']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        ax1.set_title('Overall Progress')
        
        # By subject - bar chart
        subjects = list(summary["by_subject"].keys())
        percentages = [data["percentage"] for data in summary["by_subject"].values()]
        
        bar_colors = ['#2196F3' if p < 50 else '#4CAF50' for p in percentages]
        ax2.barh(subjects, percentages, color=bar_colors)
        ax2.set_xlim(0, 100)
        ax2.set_xlabel('Completion Percentage')
        ax2.set_title('Progress by Subject')
        
        # Add percentage labels to the bars
        for i, p in enumerate(percentages):
            ax2.text(p + 1, i, f"{p}%", va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
            return True
        else:
            plt.show()
            return True
    
    def get_historical_progress(self, plan_id):
        """Get historical progress data for time-based charts"""
        try:
            # Read the progress CSV file
            csv_path = os.path.join(self.data_handler.data_dir, 'study_progress.csv')
            if not os.path.exists(csv_path):
                return None
                
            # Read CSV and filter for the specific plan
            df = pd.read_csv(csv_path)
            plan_data = df[df['plan_id'] == plan_id].copy()
            
            if plan_data.empty:
                return None
                
            # Convert timestamp to datetime
            plan_data['timestamp'] = pd.to_datetime(plan_data['timestamp'])
            plan_data = plan_data.sort_values('timestamp')
            
            # Get the study plan to know the duration and subjects
            study_plan = self.data_handler.get_study_plan(plan_id)
            if not study_plan:
                return None
                
            plan_duration = study_plan.get('plan_duration_days', 15)
            plan_start = pd.to_datetime(study_plan.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Create date range for the plan duration
            date_range = pd.date_range(start=plan_start.date(), periods=plan_duration, freq='D')
            
            # Calculate cumulative progress for each day
            daily_progress = {}
            subjects_progress = {}
            
            for date in date_range:
                date_str = date.strftime('%Y-%m-%d')
                
                # Get completed topics up to this date
                completed_up_to_date = plan_data[
                    (plan_data['timestamp'].dt.date <= date.date()) & 
                    (plan_data['completed'] == 'Yes')
                ]
                
                # Calculate overall progress
                total_topics = sum(len(subject['topics']) for subject in study_plan['subjects'])
                completed_topics = len(completed_up_to_date.drop_duplicates(['subject', 'topic']))
                
                daily_progress[date_str] = {
                    'completed': completed_topics,
                    'total': total_topics,
                    'percentage': round((completed_topics / total_topics * 100) if total_topics > 0 else 0, 1)
                }
                
                # Calculate progress by subject
                subjects_progress[date_str] = {}
                for subject in study_plan['subjects']:
                    subject_name = subject['name']
                    subject_completed = completed_up_to_date[completed_up_to_date['subject'] == subject_name]
                    subject_total = len(subject['topics'])
                    subject_completed_count = len(subject_completed.drop_duplicates(['topic']))
                    
                    subjects_progress[date_str][subject_name] = {
                        'completed': subject_completed_count,
                        'total': subject_total,
                        'percentage': round((subject_completed_count / subject_total * 100) if subject_total > 0 else 0, 1)
                    }
            
            return {
                'plan_duration': plan_duration,
                'daily_progress': daily_progress,
                'subjects_progress': subjects_progress,
                'plan_start': plan_start.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Error getting historical progress: {e}")
            return None
    
    def generate_time_based_chart(self, plan_id):
        """Generate time-based progress chart showing progress over plan duration"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
            import io
            import base64
            
            historical_data = self.get_historical_progress(plan_id)
            if not historical_data:
                return None
                
            study_plan = self.data_handler.get_study_plan(plan_id)
            if not study_plan:
                return None
                
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.patch.set_facecolor('white')
            
            # Prepare data
            dates = [datetime.strptime(date, '%Y-%m-%d') for date in historical_data['daily_progress'].keys()]
            percentages = [data['percentage'] for data in historical_data['daily_progress'].values()]
            completed_counts = [data['completed'] for data in historical_data['daily_progress'].values()]
            
            # 1. Overall Progress Over Time (Line Chart)
            ax1.plot(dates, percentages, marker='o', linewidth=2, markersize=4, color='#48bb78')
            ax1.fill_between(dates, percentages, alpha=0.3, color='#48bb78')
            ax1.set_title('Overall Progress Over Time', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Completion Percentage (%)')
            ax1.set_ylim(0, 100)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # 2. Daily Topic Completion (Bar Chart)
            daily_completed = []
            for i in range(len(completed_counts)):
                if i == 0:
                    daily_completed.append(completed_counts[i])
                else:
                    daily_completed.append(max(0, completed_counts[i] - completed_counts[i-1]))
            
            ax2.bar(dates, daily_completed, color='#667eea', alpha=0.7)
            ax2.set_title('Daily Topic Completions', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Topics Completed')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # 3. Subject-wise Progress (Stacked Area Chart)
            subjects = list(study_plan['subjects'])
            subject_names = [s['name'] for s in subjects]
            colors = plt.cm.Set3(range(len(subject_names)))
            
            # Prepare subject data 
            subject_data = {name: [] for name in subject_names}
            for date_str in historical_data['daily_progress'].keys():
                for subject_name in subject_names:
                    if subject_name in historical_data['subjects_progress'][date_str]:
                        subject_data[subject_name].append(
                            historical_data['subjects_progress'][date_str][subject_name]['percentage']
                        )
                    else:
                        subject_data[subject_name].append(0)
            
            bottom = [0] * len(dates)
            for i, (subject_name, data) in enumerate(subject_data.items()):
                ax3.fill_between(dates, bottom, [bottom[j] + data[j]/len(subject_names) for j in range(len(data))], 
                               label=subject_name, alpha=0.7, color=colors[i])
                bottom = [bottom[j] + data[j]/len(subject_names) for j in range(len(data))]
            
            ax3.set_title('Subject-wise Progress Distribution', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Progress Distribution (%)')
            ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax3.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # 4. Current Progress Summary (Pie Chart)
            current_summary = self.get_progress_summary(plan_id)
            if current_summary:
                labels = ['Completed', 'Remaining']
                sizes = [current_summary['completed_topics'], 
                        current_summary['total_topics'] - current_summary['completed_topics']]
                colors_pie = ['#48bb78', '#e2e8f0']
                wedges, texts, autotexts = ax4.pie(sizes, labels=labels, colors=colors_pie, 
                                                  autopct='%1.1f%%', startangle=90)
                ax4.set_title('Current Overall Progress', fontsize=14, fontweight='bold')
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            # Save to base64 string
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode()
            plt.close()
            
            return f'data:image/png;base64,{img_base64}'
            
        except Exception as e:
            print(f"Error generating time-based chart: {e}")
            return None