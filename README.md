# 📚 Smart Study Planner

A modern, interactive web application for creating and managing personalized study plans with progress tracking and smart notifications.

## ✨ Features

 🎯 **Core Functionality**
- **Personalized Study Plans**: Create custom study schedules based on subjects, topics, and time preferences
- **Progress Tracking**: Visual charts and analytics to monitor your learning progress
- **Smart Notifications**: Desktop reminders 15 minutes before study sessions
- **User Authentication**: Secure login system with password protection
- **Guest Mode**: Try the app without creating an account

### 🎨 **Modern UI/UX**
- **Minimal Design**: Clean, distraction-free interface
- **Interactive Charts**: Real-time progress visualization
- **Toast Notifications**: Smart feedback system
- **Mobile Responsive**: Works perfectly on all devices
- **Dark Theme**: Easy on the eyes for long study sessions

### 📊 **Analytics & Insights**
- **Summary View**: Overall progress and completion rates
- **Timeline View**: Day-by-day progress tracking
- **Subject-wise Analytics**: Detailed breakdown by subjects and topics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows/macOS/Linux

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fierycatalyst/smart-study-planner.git
   cd smart-study-planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up data files**
   ```bash
   # Copy example data files (first time only)
   copy data\users.json.example data\users.json
   copy data\study_plans.json.example data\study_plans.json
   copy data\study_progress.csv.example data\study_progress.csv
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   
   Or use the convenient batch file:
   ```bash
   run_app.bat
   ```

5. **Open in browser**
   Navigate to: `http://localhost:5000`

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Data Storage**: JSON files, CSV
- **Charts**: Matplotlib
- **Data Processing**: Pandas
- **Notifications**: Plyer
- **Styling**: Custom CSS with modern animations

## 📁 Project Structure

```
smart-study-planner/
├── app.py                     # Main Flask application
├── data_handler.py           # Data management and storage
├── notification.py           # Desktop notification system
├── progress_tracker.py       # Analytics and chart generation
├── scheduler.py              # Study plan scheduling logic
├── wsgi.py                   # Production deployment
├── requirements.txt          # Python dependencies
├── run_app.bat              # Quick start script
├── debug_test.py            # System testing and validation
├── data/                    # Data storage
│   ├── users.json.example      # Sample user data
│   ├── study_plans.json.example # Sample study plans
│   └── study_progress.csv.example # Sample progress data
├── static/                  # Frontend assets
│   ├── style.css               # Application styles
│   └── script.js               # JavaScript functionality
└── templates/               # HTML templates
    ├── index.html              # Main dashboard
    └── login.html              # Login/registration page
```

## 🎮 Usage

### Creating Your First Study Plan

1. **Register/Login**: Create an account or use guest mode
2. **Add Subjects**: Enter your subjects with priority levels
3. **Add Topics**: Break down subjects into specific topics
4. **Set Schedule**: Choose your preferred study duration (7, 15, 30, or 60 days)
5. **Start Studying**: Follow your personalized daily schedule

### Using Notifications

1. Click the notification bell icon in the dashboard
2. Enable notifications when prompted
3. Receive reminders 15 minutes before each study session
4. Stay on track with your study goals

### Tracking Progress

- **Mark topics as complete** as you finish studying them
- **View Summary charts** for overall progress
- **Check Timeline view** for daily progress tracking
- **Monitor completion rates** by subject and difficulty

## 🔧 Configuration

### Environment Setup
The app works out of the box, but you can customize:

- **Notification timing**: Modify the `minutes_before` parameter in `notification.py`
- **Chart colors**: Update color schemes in `progress_tracker.py`
- **UI themes**: Customize CSS variables in `static/style.css`

### Data Management
- User data is stored in JSON format for easy backup and portability
- Progress data is tracked in CSV format for easy analysis
- All data files are automatically created on first run

## 🧪 Testing

Run the built-in test suite to verify everything is working:

```bash
python debug_test.py
```

This will test:
- ✅ All package imports
- ✅ Data file integrity
- ✅ Flask app functionality
- ✅ Static file availability
- ✅ Notification system

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (using WSGI)
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- Desktop notifications require the `plyer` package (automatically handled)
- First-time users need to copy example data files
- Charts may take a moment to load with large datasets

## 🔮 Future Enhancements

- [ ] Export study plans to PDF
- [ ] Integration with calendar apps
- [ ] Study streak tracking
- [ ] Pomodoro timer integration
- [ ] Study group collaboration features
- [ ] Mobile app version

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/fierycatalyst/smart-study-planner/issues) page
2. Run `python debug_test.py` to diagnose problems
3. Create a new issue with detailed information


