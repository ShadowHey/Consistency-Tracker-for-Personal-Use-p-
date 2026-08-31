import time
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton)
from PySide6.QtCore import QTimer, Qt, Signal
from services.timer_service import get_running_session, start_session, pause_session, resume_session, stop_session, get_todays_sessions
from services.stats_service import get_day_boundaries
from config import THEME_COLORS

class TimerPanel(QWidget):
    timerChanged = Signal() # emitted when stopped or paused to refresh graph
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_display)
        
        self.check_recovery()
        self.refresh_display()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"""
            font-size: 48px; 
            font-weight: bold; 
            color: {THEME_COLORS['text_primary']};
            font-family: monospace;
        """)
        layout.addWidget(self.time_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        self.main_btn = QPushButton("START")
        self.main_btn.setFixedSize(120, 36)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setFixedSize(80, 36)
        self.stop_btn.setVisible(False)
        
        btn_style = f"""
            QPushButton {{
                background-color: {THEME_COLORS['border']};
                color: {THEME_COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['text_secondary']};
            }}
        """
        self.main_btn.setStyleSheet(btn_style)
        self.stop_btn.setStyleSheet(btn_style.replace(THEME_COLORS['border'], "#6E1414")) # red-ish stop
        
        self.main_btn.clicked.connect(self.on_main_action)
        self.stop_btn.clicked.connect(self.on_stop_action)
        
        btn_layout.addWidget(self.main_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)
        
    def check_recovery(self):
        # If we just launched and there's a running session, start the QTimer
        running = get_running_session()
        if running:
            self.update_timer.start(1000)
            self.main_btn.setText("PAUSE")
            self.stop_btn.setVisible(True)
            
    def get_todays_total_seconds(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        start_ts, end_ts = get_day_boundaries(today_str)
        sessions = get_todays_sessions(start_ts, end_ts)
        
        now = int(time.time())
        total = 0
        for s in sessions:
            s_start = max(s.start_timestamp, start_ts)
            s_end = min(s.end_timestamp or now, end_ts)
            if s_end > s_start:
                total += (s_end - s_start)
        return total
        
    def refresh_display(self):
        total_sec = self.get_todays_total_seconds()
        hours, rem = divmod(total_sec, 3600)
        mins, secs = divmod(rem, 60)
        self.time_label.setText(f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")
        
    def on_main_action(self):
        action = self.main_btn.text()
        if action == "START" or action == "RESUME":
            start_session()
            self.update_timer.start(1000)
            self.main_btn.setText("PAUSE")
            self.stop_btn.setVisible(True)
        elif action == "PAUSE":
            running = get_running_session()
            if running:
                pause_session(running.id)
            self.update_timer.stop()
            self.main_btn.setText("RESUME")
            self.refresh_display()
            self.timerChanged.emit()
            
    def on_stop_action(self):
        running = get_running_session()
        if running:
            stop_session(running.id)
        else:
            stop_session() # stops paused sessions
            
        self.update_timer.stop()
        self.main_btn.setText("START")
        self.stop_btn.setVisible(False)
        self.refresh_display()
        self.timerChanged.emit()
