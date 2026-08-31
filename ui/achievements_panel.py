from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QScrollArea, QFrame, QGridLayout)
from PySide6.QtCore import Qt
from config import THEME_COLORS, ACHIEVEMENT_DEFINITIONS
from services.achievement_service import get_unlocked_achievement_ids, evaluate_and_unlock_achievements, get_achievement_progress
from services.stats_service import get_contribution_data, calculate_streaks

class AchievementsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("ACHIEVEMENTS")
        header.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 24px;")
        layout.addWidget(header)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)
        
    def refresh_data(self):
        # Clear
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Evaluate new achievements
        data = get_contribution_data(365)
        stats = calculate_streaks(data)
        evaluate_and_unlock_achievements(stats)
        
        unlocked_ids = get_unlocked_achievement_ids()
        progress_map = get_achievement_progress(stats)
        
        row = 0
        col = 0
        max_cols = 3
        
        for ach in ACHIEVEMENT_DEFINITIONS:
            is_unlocked = ach['id'] in unlocked_ids
            progress = progress_map.get(ach['id'], 0)
            req = ach['requirement']
            
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {THEME_COLORS['panel']};
                    border: 1px solid {THEME_COLORS['border']};
                    border-radius: 8px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            
            title = QLabel(ach['name'])
            title_color = THEME_COLORS['gold'] if is_unlocked else THEME_COLORS['text_secondary']
            prefix = "🏆" if is_unlocked else "🔒"
            title.setText(f"{prefix} {ach['name']}")
            title.setStyleSheet(f"color: {title_color}; font-weight: bold; font-size: 16px; border: none;")
            
            desc = QLabel(ach['description'])
            desc.setWordWrap(True)
            desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px; border: none;")
            
            status = QLabel()
            if is_unlocked:
                status.setText("UNLOCKED ✓")
                status.setStyleSheet(f"color: {THEME_COLORS['green_levels'][4]}; font-weight: bold; font-size: 12px; border: none;")
            else:
                # Format progress nicely if it's seconds
                if ach['category'] in ['study_time', 'record_time']:
                    prog_h = int(progress // 3600)
                    req_h = int(req // 3600)
                    status.setText(f"{prog_h} / {req_h} hrs")
                else:
                    status.setText(f"{int(progress)} / {req}")
                status.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px; border: none;")
                
            card_layout.addWidget(title)
            card_layout.addWidget(desc)
            card_layout.addWidget(status)
            card_layout.addStretch()
            
            self.grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
