from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFrame, QSizePolicy)
from PySide6.QtCore import Qt
from datetime import datetime
from config import THEME_COLORS
from ui.timer_panel import TimerPanel
from ui.task_panel import TaskPanel
from ui.contribution_graph import ContributionGraph
from services.stats_service import calculate_day_status, get_contribution_data, calculate_streaks
from services.task_service import get_active_tasks, get_completed_task_ids

class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_stats()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        
        today_layout = QVBoxLayout()
        today_label = QLabel("TODAY")
        today_label.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        
        date_label = QLabel(datetime.now().strftime("%B %d, %Y"))
        date_label.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 24px;")
        
        today_layout.addWidget(today_label)
        today_layout.addWidget(date_label)
        header_layout.addLayout(today_layout)
        header_layout.addStretch()
        
        # Streak indicator
        self.streak_label = QLabel("🔥 0 DAY STREAK")
        self.streak_label.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 16px;")
        header_layout.addWidget(self.streak_label)
        
        layout.addLayout(header_layout)
        
        # --- STATS SUMMARY ---
        stats_layout = QHBoxLayout()
        
        study_layout = QVBoxLayout()
        study_title = QLabel("Study Time")
        study_title.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        self.study_val = QLabel("00:00:00")
        self.study_val.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 16px; font-weight: bold;")
        study_layout.addWidget(study_title)
        study_layout.addWidget(self.study_val)
        
        tasks_layout = QVBoxLayout()
        tasks_title = QLabel("Tasks")
        tasks_title.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        self.tasks_val = QLabel("0 / 0")
        self.tasks_val.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 16px; font-weight: bold;")
        tasks_layout.addWidget(tasks_title)
        tasks_layout.addWidget(self.tasks_val)
        
        stats_layout.addLayout(study_layout)
        stats_layout.addSpacing(40)
        stats_layout.addLayout(tasks_layout)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.HLine)
        div1.setStyleSheet(f"background-color: {THEME_COLORS['border']};")
        layout.addWidget(div1)
        
        # --- TIMER & TASKS ---
        content_layout = QHBoxLayout()
        
        # Timer (Left)
        self.timer_panel = TimerPanel()
        self.timer_panel.timerChanged.connect(self.on_activity_changed)
        content_layout.addWidget(self.timer_panel, stretch=1)
        
        # Tasks (Right)
        self.task_panel = TaskPanel()
        self.task_panel.taskChanged.connect(self.on_activity_changed)
        content_layout.addWidget(self.task_panel, stretch=1)
        
        layout.addLayout(content_layout)
        
        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setStyleSheet(f"background-color: {THEME_COLORS['border']};")
        layout.addWidget(div2)
        
        # --- CONTRIBUTIONS ---
        contributions_label = QLabel("CONTRIBUTIONS")
        contributions_label.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        layout.addWidget(contributions_label)
        
        self.graph = ContributionGraph()
        layout.addWidget(self.graph)
        
        layout.addStretch()
        
    def refresh_stats(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        status = calculate_day_status(today_str)
        
        # Update tasks text
        total_tasks = len(get_active_tasks())
        self.tasks_val.setText(f"{status['completed_tasks']} / {total_tasks}")
        
        # Update study time text
        total_sec = status['study_seconds']
        hours, rem = divmod(total_sec, 3600)
        mins, secs = divmod(rem, 60)
        self.study_val.setText(f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")
        
        # Update streak
        data = get_contribution_data(365)
        streaks = calculate_streaks(data)
        self.streak_label.setText(f"🔥 {streaks['current_active']} DAY STREAK")
        
    def on_activity_changed(self):
        self.refresh_stats()
        self.graph.refresh_data()
