from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFrame)
from PySide6.QtCore import Qt
from config import THEME_COLORS
from services.stats_service import get_contribution_data, calculate_streaks
from services.achievement_service import get_unlocked_achievement_ids

class ProfilePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignTop)
        
        header = QLabel("PROFILE")
        header.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 24px;")
        layout.addWidget(header)
        layout.addSpacing(20)
        
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setSpacing(15)
        layout.addWidget(self.stats_container)
        
    def add_stat_row(self, label, value):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 16px;")
        val = QLabel(str(value))
        val.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 16px;")
        val.setAlignment(Qt.AlignRight)
        
        row.addWidget(lbl)
        row.addWidget(val)
        self.stats_layout.addLayout(row)
        
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background-color: {THEME_COLORS['border']};")
        self.stats_layout.addWidget(div)
        
    def refresh_data(self):
        # Clear
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # simplified clearing for rows
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
        data = get_contribution_data(365)
        stats = calculate_streaks(data)
        badges = len(get_unlocked_achievement_ids())
        
        total_sec = stats['total_study']
        hours, rem = divmod(total_sec, 3600)
        mins, _ = divmod(rem, 60)
        study_str = f"{int(hours)}h {int(mins)}m"
        
        self.add_stat_row("Study Streak", f"🔥 {stats['current_active']} days")
        self.add_stat_row("Longest Streak", f"🔥 {stats['max_active']} days")
        self.add_stat_row("Total Study Time", study_str)
        self.add_stat_row("Total Tasks", stats['total_tasks'])
        self.add_stat_row("Green Days", stats['green_days_count'])
        self.add_stat_row("Red Days", stats['red_days_count'])
        self.add_stat_row("Badges", badges)
