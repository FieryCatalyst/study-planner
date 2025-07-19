// Global variables
let currentPlanId = null;
let notificationsEnabled = false;
let currentPlanData = null;

// DOM elements
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const studyPlanForm = document.getElementById('study-plan-form');
const subjectsContainer = document.getElementById('subjects-container');
const addSubjectBtn = document.getElementById('add-subject');
const loadingOverlay = document.getElementById('loading-overlay');
const notificationsToggle = document.getElementById('notifications-toggle');
const themeToggle = document.getElementById('theme-toggle');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Study Planner...');
    initializeTabs();
    initializeForm();
    initializeTheme();
    initializeUserProfile();
    initializePlanManagement();
    initializeChartControls();
    initializeNotificationButton();
    loadLatestPlan();
    
    // Add event listeners with null checks
    if (studyPlanForm) {
        studyPlanForm.addEventListener('submit', handleFormSubmit);
    }
    if (addSubjectBtn) {
        addSubjectBtn.addEventListener('click', addSubject);
    }
    if (notificationsToggle) {
        notificationsToggle.addEventListener('click', toggleNotifications);
    }
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Add logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    console.log('Study Planner initialized successfully!');
});

// Tab functionality
function initializeTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update active tab button
    tabButtons.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // Update active tab content
    tabContents.forEach(content => content.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    
    // Load data for specific tabs
    if (tabId === 'dashboard' && currentPlanId) {
        loadDashboard();
    } else if (tabId === 'schedule' && currentPlanId) {
        loadSchedule();
    } else if (tabId === 'progress' && currentPlanId) {
        loadProgress();
    }
}

// Form initialization
function initializeForm() {
    addSubject(); // Add initial subject
}

// Theme functionality
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('i');
    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

// User authentication functions
function initializeUserProfile() {
    const userProfile = document.querySelector('.user-profile');
    const username = userProfile ? userProfile.getAttribute('data-username') : null;
    
    if (username) {
        console.log(`Welcome, ${username}!`);
    } else {
        // Check if user is logged in
        fetch('/api/user-status')
            .then(response => response.json())
            .then(data => {
                if (!data.logged_in) {
                    window.location.href = '/login';
                }
            })
            .catch(error => {
                console.error('Error checking user status:', error);
            });
    }
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        fetch('/api/logout', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/login';
                } else {
                    showToast('Error logging out', 'error');
                }
            })
            .catch(error => {
                console.error('Error logging out:', error);
                showToast('Error logging out', 'error');
            });
    }
}

// Subject management
function addSubject() {
    const subjectDiv = document.createElement('div');
    subjectDiv.className = 'subject-item';
    subjectDiv.innerHTML = `
        <button type="button" class="remove-subject" onclick="removeSubject(this)">
            <i class="fas fa-times"></i>
        </button>
        <div class="subject-header">
            <input type="text" placeholder="Subject name (e.g., Mathematics)" required>
            <select required>
                <option value="">Select Priority</option>
                <option value="1">Low Priority</option>
                <option value="2">Medium Priority</option>
                <option value="3">High Priority</option>
                <option value="4">Very High Priority</option>
                <option value="5">Critical Priority</option>
            </select>
        </div>
        <div class="topics-container">
            <div class="topic-item">
                <input type="text" placeholder="Topic name" required>
                <select>
                    <option value="easy">Easy</option>
                    <option value="medium" selected>Medium</option>
                    <option value="hard">Hard</option>
                </select>
                <button type="button" class="remove-topic" onclick="removeTopic(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        <button type="button" class="btn btn-outline add-topic" onclick="addTopic(this)">
            <i class="fas fa-plus"></i> Add Topic
        </button>
    `;
    subjectsContainer.appendChild(subjectDiv);
}

function removeSubject(button) {
    if (subjectsContainer.children.length > 1) {
        button.parentElement.remove();
    } else {
        showToast('⚠️ At least one subject is required!', 'warning');
    }
}

function addTopic(button) {
    const topicsContainer = button.previousElementSibling;
    const topicDiv = document.createElement('div');
    topicDiv.className = 'topic-item';
    topicDiv.innerHTML = `
        <input type="text" placeholder="Topic name" required>
        <select>
            <option value="easy">Easy</option>
            <option value="medium" selected>Medium</option>
            <option value="hard">Hard</option>
        </select>
        <button type="button" class="remove-topic" onclick="removeTopic(this)">
            <i class="fas fa-trash"></i>
        </button>
    `;
    topicsContainer.appendChild(topicDiv);
}

function removeTopic(button) {
    const topicsContainer = button.parentElement.parentElement;
    if (topicsContainer.children.length > 1) {
        button.parentElement.remove();
    } else {
        showToast('⚠️ At least one topic is required per subject!', 'warning');
    }
}

// Form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');
    
    // Validate form data
    const formData = collectFormData();
    console.log('Collected form data:', formData);
    
    if (!validateFormData(formData)) {
        console.log('Form validation failed');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log('Sending API request to create plan...');
        const response = await fetch('/api/create-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('HTTP Error:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('API response:', result);
        
        if (result.success) {
            currentPlanId = result.plan_id;
            clearSessionToasts(); // Clear previous session toasts for fresh feedback
            showToast('🎉 Study plan created successfully!', 'success');
            
            // Auto-switch to dashboard and load it
            setTimeout(() => {
                switchTab('dashboard');
                loadDashboard();
            }, 1000);
        } else {
            showToast('❌ Error creating study plan: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error creating study plan:', error);
        showToast('❌ Network error: Check if the server is running on localhost:5000', 'error');
    } finally {
        showLoading(false);
    }
}

function validateFormData(formData) {
    if (formData.subjects.length === 0) {
        showToast('⚠️ Please add at least one subject', 'warning');
        return false;
    }
    
    if (formData.time_available_per_day < 1) {
        showToast('⚠️ Please set a valid daily study time', 'warning');
        return false;
    }
    
    if (formData.preferred_time_slots.length === 0) {
        showToast('⚠️ Please set at least one time slot', 'warning');
        return false;
    }
    
    return true;
}

function collectFormData() {
    const timeAvailable = parseInt(document.getElementById('time-available').value);
    const planDuration = parseInt(document.getElementById('plan-duration').value) || 15;
    
    // Collect time slots
    const timeSlots = [];
    for (let i = 1; i <= 3; i++) {
        const start = document.getElementById(`slot${i}-start`).value;
        const end = document.getElementById(`slot${i}-end`).value;
        if (start && end) {
            timeSlots.push(`${start}-${end}`);
        }
    }
    
    // Collect subjects
    const subjects = [];
    const subjectItems = document.querySelectorAll('.subject-item');
    
    subjectItems.forEach(item => {
        const nameInput = item.querySelector('.subject-header input[type="text"]');
        const weightSelect = item.querySelector('.subject-header select');
        const topicInputs = item.querySelectorAll('.topic-item input[type="text"]');
        const difficultySelects = item.querySelectorAll('.topic-item select');
        
        const topics = [];
        topicInputs.forEach((input, index) => {
            if (input.value.trim()) {
                topics.push({
                    name: input.value.trim(),
                    difficulty: difficultySelects[index].value
                });
            }
        });
        
        if (nameInput.value.trim() && weightSelect.value && topics.length > 0) {
            subjects.push({
                name: nameInput.value.trim(),
                weight: parseInt(weightSelect.value),
                topics: topics
            });
        }
    });
    
    return {
        subjects: subjects,
        time_available_per_day: timeAvailable,
        preferred_time_slots: timeSlots,
        plan_duration_days: planDuration
    };
}

// Load latest plan on page load
async function loadLatestPlan() {
    try {
        const response = await fetch('/api/get-latest-plan');
        const result = await response.json();
        
        if (result.success) {
            currentPlanId = result.plan_id;
            currentPlanData = result.study_plan;
            updateDashboardPlaceholders();
            updateCurrentPlanInfo();
        } else {
            console.log('No existing plans found - ready to create new plan');
        }
    } catch (error) {
        console.log('No existing plans found - ready to create new plan');
    }
}

// Initialize plan management
function initializePlanManagement() {
    const viewAllPlansBtn = document.getElementById('view-all-plans');
    const deleteCurrentPlanBtn = document.getElementById('delete-current-plan');
    const scheduleViewSelect = document.getElementById('schedule-view');
    const refreshScheduleBtn = document.getElementById('refresh-schedule');
    
    if (viewAllPlansBtn) {
        viewAllPlansBtn.addEventListener('click', showPlansModal);
    }
    
    if (deleteCurrentPlanBtn) {
        deleteCurrentPlanBtn.addEventListener('click', deleteCurrentPlan);
    }
    
    if (scheduleViewSelect) {
        scheduleViewSelect.addEventListener('change', filterScheduleView);
    }
    
    if (refreshScheduleBtn) {
        refreshScheduleBtn.addEventListener('click', () => {
            loadSchedule();
            showToast('📅 Schedule refreshed', 'success');
        });
    }
}

// Update current plan info in dashboard
function updateCurrentPlanInfo() {
    if (!currentPlanData || !currentPlanId) {
        document.getElementById('current-plan-name').textContent = 'No plan selected';
        document.getElementById('current-plan-duration').textContent = '-';
        document.getElementById('current-plan-date').textContent = '-';
        return;
    }
    
    const planName = `Study Plan (${currentPlanData.subjects?.length || 0} subjects)`;
    const duration = `${currentPlanData.plan_duration_days || 15} days`;
    const createdDate = currentPlanData.created_at ? 
        new Date(currentPlanData.created_at).toLocaleDateString() : 'Unknown';
    
    document.getElementById('current-plan-name').textContent = planName;
    document.getElementById('current-plan-duration').textContent = duration;
    document.getElementById('current-plan-date').textContent = createdDate;
}

// Show all plans modal
async function showPlansModal() {
    const modal = document.getElementById('plans-modal');
    const plansList = document.getElementById('plans-list');
    
    modal.style.display = 'block';
    plansList.innerHTML = `
        <div class="loading-placeholder">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading plans...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/get-all-plans');
        const result = await response.json();
        
        if (result.success) {
            displayPlansInModal(result.plans);
        } else {
            plansList.innerHTML = `
                <div class="error-placeholder">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading plans: ${result.error}</p>
                </div>
            `;
        }
    } catch (error) {
        plansList.innerHTML = `
            <div class="error-placeholder">
                <i class="fas fa-exclamation-circle"></i>
                <p>Error loading plans: ${error.message}</p>
            </div>
        `;
    }
}

function displayPlansInModal(plans) {
    const plansList = document.getElementById('plans-list');
    
    if (plans.length === 0) {
        plansList.innerHTML = `
            <div class="empty-placeholder">
                <i class="fas fa-folder-open"></i>
                <p>No study plans found</p>
                <small>Create your first plan in the Create Plan tab</small>
            </div>
        `;
        return;
    }
    
    plansList.innerHTML = plans.map(plan => `
        <div class="plan-item ${plan.plan_id === currentPlanId ? 'active' : ''}">
            <div class="plan-info">
                <h4>Study Plan - ${plan.subjects_count} subjects</h4>
                <div class="plan-details">
                    <span><i class="fas fa-calendar"></i> ${plan.duration_days} days</span>
                    <span><i class="fas fa-book"></i> ${plan.total_topics} topics</span>
                    <span><i class="fas fa-clock"></i> ${plan.time_per_day}h/day</span>
                </div>
                <small>Created: ${new Date(plan.created_at).toLocaleDateString()}</small>
            </div>
            <div class="plan-actions">
                <button class="btn btn-primary btn-sm" onclick="selectPlan('${plan.plan_id}')">
                    ${plan.plan_id === currentPlanId ? 'Current' : 'Select'}
                </button>
                <button class="btn btn-danger btn-sm" onclick="deletePlan('${plan.plan_id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function closePlansModal() {
    document.getElementById('plans-modal').style.display = 'none';
}

async function selectPlan(planId) {
    try {
        showLoading(true);
        const response = await fetch(`/api/get-plan/${planId}`);
        const result = await response.json();
        
        if (result.success) {
            currentPlanId = planId;
            currentPlanData = result.study_plan;
            updateCurrentPlanInfo();
            updateDashboardPlaceholders();
            closePlansModal();
            
            // Refresh current tab if it's dashboard, schedule, or progress
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab) {
                const tabId = activeTab.id;
                if (tabId === 'dashboard') loadDashboard();
                else if (tabId === 'schedule') loadSchedule();
                else if (tabId === 'progress') loadProgress();
            }
            
            showToast('📋 Study plan selected successfully', 'success');
        } else {
            showToast('❌ Error selecting plan: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('❌ Error selecting plan: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function deletePlan(planId) {
    if (!confirm('Are you sure you want to delete this study plan? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading(true);
        const response = await fetch(`/api/delete-plan/${planId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.success) {
            // If we deleted the current plan, clear it
            if (planId === currentPlanId) {
                currentPlanId = null;
                currentPlanData = null;
                updateCurrentPlanInfo();
                updateDashboardPlaceholders();
            }
            
            // Refresh the modal
            showPlansModal();
            showToast('🗑️ Study plan deleted successfully', 'success');
        } else {
            showToast('❌ Error deleting plan: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('❌ Error deleting plan: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteCurrentPlan() {
    if (!currentPlanId) {
        showToast('⚠️ No plan selected to delete', 'warning');
        return;
    }
    
    await deletePlan(currentPlanId);
}

// Dashboard functionality
async function loadDashboard() {
    if (!currentPlanId) {
        return;
    }
    
    try {
        showLoading(true);
        
        // Load current plan data if not already loaded
        if (!currentPlanData) {
            const planResponse = await fetch(`/api/get-plan/${currentPlanId}`);
            const planResult = await planResponse.json();
            if (planResult.success) {
                currentPlanData = planResult.study_plan;
                updateCurrentPlanInfo();
            }
        }
        
        // Load progress summary
        const summaryResponse = await fetch(`/api/progress-summary/${currentPlanId}`);
        const summaryResult = await summaryResponse.json();
        
        if (summaryResult.success) {
            updateDashboardStats(summaryResult.summary);
        } else {
            showToast('Error loading progress summary: ' + summaryResult.error, 'error');
        }
        
        // Load progress chart based on current view
        const staticBtn = document.getElementById('static-chart-btn');
        const timelineBtn = document.getElementById('timeline-chart-btn');
        
        if (timelineBtn && timelineBtn.classList.contains('active')) {
            loadTimelineChart();
        } else {
            loadStaticChart();
        }
    } catch (error) {
        showToast('Error loading dashboard: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function showChartPlaceholder() {
    const chartImg = document.getElementById('progress-chart');
    const chartPlaceholder = document.getElementById('chart-placeholder');
    
    chartImg.style.display = 'none';
    chartPlaceholder.style.display = 'block';
    chartPlaceholder.innerHTML = `
        <i class="fas fa-chart-bar"></i>
        <p>Chart visualization requires matplotlib</p>
        <small>Install with: pip install matplotlib</small>
    `;
}

function updateDashboardStats(summary) {
    // Update progress circle
    const progressPercentage = document.getElementById('progress-percentage');
    const progressCircle = document.querySelector('.progress-circle');
    
    progressPercentage.textContent = `${summary.completion_percentage}%`;
    
    // Update progress circle background
    const angle = (summary.completion_percentage / 100) * 360;
    progressCircle.style.background = `conic-gradient(var(--primary-color) ${angle}deg, var(--bg-tertiary) ${angle}deg)`;
    
    // Update quick stats
    document.getElementById('completed-topics').textContent = summary.completed_topics;
    document.getElementById('total-subjects').textContent = summary.total_subjects;
    document.getElementById('total-topics').textContent = summary.total_topics;
}

function updateProgressChart(chartData) {
    const chartImg = document.getElementById('progress-chart');
    const chartPlaceholder = document.getElementById('chart-placeholder');
    const chartLoading = document.getElementById('chart-loading');
    
    chartImg.src = chartData;
    chartImg.style.display = 'block';
    chartPlaceholder.style.display = 'none';
    chartLoading.style.display = 'none';
}

// Chart Controls Functionality
function initializeChartControls() {
    const staticChartBtn = document.getElementById('static-chart-btn');
    const timelineChartBtn = document.getElementById('timeline-chart-btn');
    
    if (staticChartBtn) {
        staticChartBtn.addEventListener('click', () => switchChartView('static'));
    }
    if (timelineChartBtn) {
        timelineChartBtn.addEventListener('click', () => switchChartView('timeline'));
    }
}

function switchChartView(viewType) {
    const staticBtn = document.getElementById('static-chart-btn');
    const timelineBtn = document.getElementById('timeline-chart-btn');
    
    // Update button states
    staticBtn.classList.toggle('active', viewType === 'static');
    timelineBtn.classList.toggle('active', viewType === 'timeline');
    
    // Load appropriate chart
    if (currentPlanId) {
        if (viewType === 'static') {
            loadStaticChart();
        } else if (viewType === 'timeline') {
            loadTimelineChart();
        }
    }
}

async function loadStaticChart() {
    if (!currentPlanId) return;
    
    try {
        showChartLoading(true);
        
        const chartResponse = await fetch(`/api/progress-chart/${currentPlanId}`);
        const chartResult = await chartResponse.json();
        
        if (chartResult.success) {
            updateProgressChart(chartResult.chart);
        } else {
            showChartPlaceholder();
        }
    } catch (error) {
        console.error('Error loading static chart:', error);
        showChartPlaceholder();
    } finally {
        showChartLoading(false);
    }
}

async function loadTimelineChart() {
    if (!currentPlanId) return;
    
    try {
        showChartLoading(true);
        
        const chartResponse = await fetch(`/api/progress-chart-timeline/${currentPlanId}`);
        const chartResult = await chartResponse.json();
        
        if (chartResult.success) {
            updateProgressChart(chartResult.chart);
        } else {
            showChartError('Timeline chart unavailable - need historical data');
        }
    } catch (error) {
        console.error('Error loading timeline chart:', error);
        showChartError('Error loading timeline chart');
    } finally {
        showChartLoading(false);
    }
}

function showChartLoading(show) {
    const chartLoading = document.getElementById('chart-loading');
    const chartImg = document.getElementById('progress-chart');
    const chartPlaceholder = document.getElementById('chart-placeholder');
    
    if (show) {
        chartLoading.style.display = 'block';
        chartImg.style.display = 'none';
        chartPlaceholder.style.display = 'none';
    } else {
        chartLoading.style.display = 'none';
    }
}

function showChartError(message) {
    const chartImg = document.getElementById('progress-chart');
    const chartPlaceholder = document.getElementById('chart-placeholder');
    const chartLoading = document.getElementById('chart-loading');
    
    chartImg.style.display = 'none';
    chartLoading.style.display = 'none';
    chartPlaceholder.style.display = 'block';
    chartPlaceholder.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <p>${message}</p>
    `;
}

function updateDashboardPlaceholders() {
    const placeholders = document.querySelectorAll('.chart-placeholder, .schedule-placeholder, .progress-placeholder');
    placeholders.forEach(placeholder => {
        if (currentPlanId) {
            placeholder.style.display = 'none';
        } else {
            placeholder.style.display = 'block';
        }
    });
}

// Schedule functionality
async function loadSchedule() {
    if (!currentPlanId) {
        return;
    }
    
    try {
        showLoading(true);
        const response = await fetch(`/api/get-plan/${currentPlanId}`);
        const result = await response.json();
        
        if (result.success) {
            displaySchedule(result.study_plan.daily_schedule, result.study_plan);
        } else {
            showToast('❌ Error loading schedule: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('❌ Error loading schedule: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displaySchedule(dailySchedule, planData) {
    const container = document.getElementById('schedule-container');
    container.innerHTML = '';
    
    const sortedDates = Object.keys(dailySchedule).sort();
    
    if (sortedDates.length === 0) {
        container.innerHTML = `
            <div class="schedule-placeholder">
                <i class="fas fa-calendar-plus"></i>
                <p>No schedule items found</p>
            </div>
        `;
        return;
    }
    
    // Update schedule stats
    updateScheduleStats(sortedDates, dailySchedule, planData);
    
    // Filter dates based on selected view
    const filteredDates = filterScheduleDates(sortedDates);
    
    if (filteredDates.length === 0) {
        container.innerHTML = `
            <div class="schedule-placeholder">
                <i class="fas fa-filter"></i>
                <p>No schedule items in selected view</p>
                <small>Try changing the view filter above</small>
            </div>
        `;
        return;
    }
    
    filteredDates.forEach(date => {
        const scheduleItems = dailySchedule[date];
        if (scheduleItems.length === 0) return;
        
        const dayDiv = document.createElement('div');
        dayDiv.className = 'schedule-day';
        
        const dateObj = new Date(date);
        const today = new Date();
        const isToday = dateObj.toDateString() === today.toDateString();
        const isPast = dateObj < today && !isToday;
        const isUpcoming = dateObj > today;
        
        const dateFormatted = dateObj.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        let dateStatus = '';
        if (isToday) dateStatus = '<span class="date-badge today">Today</span>';
        else if (isPast) dateStatus = '<span class="date-badge past">Past</span>';
        else if (isUpcoming) dateStatus = '<span class="date-badge upcoming">Upcoming</span>';
        
        dayDiv.innerHTML = `
            <div class="schedule-date">
                <div class="schedule-date-main">
                    <i class="fas fa-calendar-day"></i>
                    ${dateFormatted}
                </div>
                ${dateStatus}
            </div>
            <div class="schedule-items">
                ${scheduleItems.map(item => `
                    <div class="schedule-item ${isPast ? 'past' : ''}">
                        <div class="schedule-item-content">
                            <h4>${item.subject}</h4>
                            <p>${item.topic}</p>
                            ${item.priority ? `<span class="priority-badge priority-${item.priority}">Priority ${item.priority}</span>` : ''}
                        </div>
                        <div class="schedule-item-time">
                            <i class="fas fa-clock"></i>
                            ${item.time_slot}
                            <small>${item.duration || '2 hours'}</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.appendChild(dayDiv);
    });
}

function updateScheduleStats(allDates, dailySchedule, planData) {
    const totalDays = allDates.length;
    const totalSessions = allDates.reduce((sum, date) => sum + dailySchedule[date].length, 0);
    const planDuration = planData.plan_duration_days || totalDays;
    
    document.getElementById('schedule-total-days').textContent = totalDays;
    document.getElementById('schedule-total-sessions').textContent = totalSessions;
    document.getElementById('schedule-duration').textContent = `${planDuration} days`;
}

function filterScheduleDates(allDates) {
    const viewFilter = document.getElementById('schedule-view').value;
    const today = new Date();
    
    switch (viewFilter) {
        case 'week':
            const weekStart = new Date(today);
            weekStart.setDate(today.getDate() - today.getDay()); // Start of week (Sunday)
            const weekEnd = new Date(weekStart);
            weekEnd.setDate(weekStart.getDate() + 6); // End of week (Saturday)
            
            return allDates.filter(date => {
                const dateObj = new Date(date);
                return dateObj >= weekStart && dateObj <= weekEnd;
            });
            
        case 'month':
            const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
            const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
            
            return allDates.filter(date => {
                const dateObj = new Date(date);
                return dateObj >= monthStart && dateObj <= monthEnd;
            });
            
        case 'upcoming':
            const upcomingEnd = new Date(today);
            upcomingEnd.setDate(today.getDate() + 7);
            
            return allDates.filter(date => {
                const dateObj = new Date(date);
                return dateObj >= today && dateObj <= upcomingEnd;
            });
            
        default: // 'all'
            return allDates;
    }
}

function filterScheduleView() {
    if (currentPlanId) {
        loadSchedule();
    }
}

// Progress tracking functionality
async function loadProgress() {
    if (!currentPlanId) {
        return;
    }
    
    try {
        showLoading(true);
        const response = await fetch(`/api/get-plan/${currentPlanId}`);
        const result = await response.json();
        
        if (result.success) {
            displayProgress(result.study_plan.subjects);
            showToast('📊 Progress loaded successfully!', 'success');
        } else {
            showToast('❌ Error loading progress: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('❌ Error loading progress: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayProgress(subjects) {
    const container = document.getElementById('progress-container');
    container.innerHTML = '';
    
    if (!subjects || subjects.length === 0) {
        container.innerHTML = `
            <div class="progress-placeholder">
                <i class="fas fa-clipboard-list"></i>
                <p>No subjects found in your study plan</p>
            </div>
        `;
        return;
    }
    
    subjects.forEach(subject => {
        const subjectDiv = document.createElement('div');
        subjectDiv.className = 'progress-subject';
        
        subjectDiv.innerHTML = `
            <h3>${subject.name}</h3>
            <div class="progress-topics">
                ${subject.topics.map(topic => `
                    <div class="progress-topic ${topic.completed ? 'completed' : ''}">
                        <div class="progress-topic-info">
                            <h4>${topic.name}</h4>
                            <p>Difficulty: ${topic.difficulty || 'Medium'}</p>
                        </div>
                        <input 
                            type="checkbox" 
                            class="progress-checkbox"
                            ${topic.completed ? 'checked' : ''}
                            onchange="updateTopicProgress('${subject.name}', '${topic.name}', this.checked)"
                        >
                    </div>
                `).join('')}
            </div>
        `;
        
        container.appendChild(subjectDiv);
    });
}

// Update topic progress
async function updateTopicProgress(subject, topic, completed) {
    if (!currentPlanId) return;
    
    try {
        const response = await fetch('/api/update-progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                plan_id: currentPlanId,
                subject: subject,
                topic: topic,
                completed: completed
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`✅ Progress updated for ${topic}`, 'success');
            // Refresh dashboard if it's active
            if (document.getElementById('dashboard').classList.contains('active')) {
                setTimeout(() => loadDashboard(), 500);
            }
        } else {
            showToast('❌ Error updating progress', 'error');
        }
    } catch (error) {
        showToast('❌ Error updating progress: ' + error.message, 'error');
    }
}

// Notifications functionality
async function toggleNotifications() {
    if (!currentPlanId) {
        showNotificationToast('Please create a study plan first', 'warning');
        return;
    }
    
    const button = document.getElementById('notifications-toggle');
    
    try {
        // Add loading state
        button.classList.add('loading');
        
        if (notificationsEnabled) {
            const response = await fetch('/api/notifications/stop', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                notificationsEnabled = false;
                updateNotificationButton();
                showNotificationToast('🔕 Notifications disabled', 'info');
            } else {
                showNotificationToast('Failed to disable notifications', 'error');
            }
        } else {
            const response = await fetch('/api/notifications/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan_id: currentPlanId,
                    minutes_before: 15
                })
            });
            const result = await response.json();
            
            if (result.success) {
                notificationsEnabled = true;
                updateNotificationButton();
                showNotificationToast('🔔 Notifications enabled! You\'ll be reminded 15 minutes before study sessions.', 'success');
                
                // Show notification indicator activity
                showNotificationActivity();
            } else {
                showNotificationToast('Failed to enable notifications', 'error');
            }
        }
    } catch (error) {
        console.error('Notification error:', error);
        showNotificationToast('Error toggling notifications. Please try again.', 'error');
    } finally {
        // Remove loading state with slight delay for smooth animation
        setTimeout(() => {
            button.classList.remove('loading');
        }, 300);
    }
}

function updateNotificationButton() {
    const button = document.getElementById('notifications-toggle');
    const icon = button.querySelector('i');
    const status = button.querySelector('.notification-status');
    
    if (notificationsEnabled) {
        icon.className = 'fas fa-bell';
        button.classList.add('active');
        button.title = 'Notifications On - Click to disable';
        status.classList.add('show');
        
        // Add periodic pulse animation
        setInterval(() => {
            if (notificationsEnabled) {
                status.style.animation = 'notification-dot-pulse 1s ease-in-out';
                setTimeout(() => {
                    if (status) status.style.animation = '';
                }, 1000);
            }
        }, 5000);
    } else {
        icon.className = 'fas fa-bell-slash';
        button.classList.remove('active');
        button.title = 'Notifications Off - Click to enable';
        status.classList.remove('show');
    }
}

function showNotificationActivity() {
    const status = document.querySelector('.notification-status');
    if (status) {
        status.style.background = '#10b981';
        status.style.animation = 'notification-dot-pulse 0.6s ease-in-out 3';
        
        setTimeout(() => {
            status.style.background = '#ef4444';
            status.style.animation = '';
        }, 2000);
    }
}

// Enhanced toast notification system
function showNotificationToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 5000);
    
    // Remove empty container
    setTimeout(() => {
        if (toastContainer && toastContainer.children.length === 0) {
            toastContainer.remove();
        }
    }, 5500);
}

// Initialize notification button state
function initializeNotificationButton() {
    const button = document.getElementById('notifications-toggle');
    if (button) {
        // Add hover effect enhancement
        button.addEventListener('mouseenter', () => {
            if (notificationsEnabled) {
                button.style.transform = 'translateY(-3px) scale(1.05)';
            }
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = '';
        });
        
        // Initialize state
        updateNotificationButton();
    }
}

// Utility functions
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

// Toast tracking system
let shownToasts = new Set();
let sessionToasts = new Set();

// Function to clear session toasts (use when user performs major actions)
function clearSessionToasts() {
    sessionToasts.clear();
}

function showToast(message, type = 'success', options = {}) {
    const { 
        forceShow = false, 
        oncePerSession = false, 
        onceEver = false 
    } = options;
    
    const toastKey = `${type}:${message}`;
    
    // Check if this toast should be suppressed
    if (!forceShow) {
        if (onceEver && shownToasts.has(toastKey)) {
            return; // Don't show if already shown in this session
        }
        if (oncePerSession && sessionToasts.has(toastKey)) {
            return; // Don't show if already shown in this session
        }
    }
    
    // Add to tracking sets
    if (onceEver) shownToasts.add(toastKey);
    if (oncePerSession) sessionToasts.add(toastKey);
    
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle'
    };
    
    toast.innerHTML = `
        <i class="toast-icon ${iconMap[type]}"></i>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="removeToast(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            removeToast(toast.querySelector('.toast-close'));
        }
    }, 5000);
}

function removeToast(button) {
    const toast = button.parentElement;
    toast.style.animation = 'slideOut 0.3s ease-in-out';
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Dynamic CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
