from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QCheckBox, 
                               QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal
from datetime import datetime
from services.task_service import get_active_tasks, get_completed_task_ids, add_task, toggle_task_completion
from config import THEME_COLORS

class TaskPanel(QWidget):
    # Signal emitted when a task is toggled, to tell other widgets (like the graph) to refresh
    taskChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_tasks()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("TODAY'S TASKS")
        header.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        layout.addWidget(header)
        
        # Add task input
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add new task...")
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME_COLORS['background']};
                color: {THEME_COLORS['text_primary']};
                border: 1px solid {THEME_COLORS['border']};
                border-radius: 4px;
                padding: 6px;
            }}
        """)
        self.task_input.returnPressed.connect(self.on_add_task)
        
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['border']};
                color: {THEME_COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['text_secondary']};
            }}
        """)
        add_btn.clicked.connect(self.on_add_task)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)
        
        # Task List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setContentsMargins(0, 10, 0, 0)
        
        self.scroll_area.setWidget(self.list_container)
        layout.addWidget(self.scroll_area)
        
    def on_add_task(self):
        name = self.task_input.text().strip()
        if name:
            add_task(name)
            self.task_input.clear()
            self.refresh_tasks()
            
    def refresh_tasks(self):
        # Clear existing
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        today_str = datetime.now().strftime("%Y-%m-%d")
        tasks = get_active_tasks()
        completed_ids = get_completed_task_ids(today_str)
        
        for t in tasks:
            cb = QCheckBox(t.name)
            is_completed = t.id in completed_ids
            cb.setChecked(is_completed)
            
            # Styling
            color = THEME_COLORS['text_secondary'] if is_completed else THEME_COLORS['text_primary']
            strike = "line-through" if is_completed else "none"
            
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    text-decoration: {strike};
                    font-size: 14px;
                    padding: 4px 0;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {THEME_COLORS['border']};
                    border-radius: 8px; /* makes it circle */
                    background-color: {THEME_COLORS['background']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {THEME_COLORS['green_levels'][4]};
                    border: 1px solid {THEME_COLORS['green_levels'][4]};
                }}
            """)
            
            # Connect
            cb.clicked.connect(lambda checked, tid=t.id, cbox=cb: self.on_task_toggled(tid, cbox))
            self.list_layout.addWidget(cb)
            
    def on_task_toggled(self, task_id, checkbox):
        today_str = datetime.now().strftime("%Y-%m-%d")
        toggle_task_completion(task_id, today_str)
        self.refresh_tasks()
        self.taskChanged.emit()
