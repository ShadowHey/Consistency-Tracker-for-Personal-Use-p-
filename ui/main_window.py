from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QApplication)
from PySide6.QtCore import Qt
from config import THEME_COLORS
from ui.dashboard import Dashboard
from ui.achievements_panel import AchievementsPanel
from ui.profile_panel import ProfilePanel
from ui.settings_panel import SettingsPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Tracker")
        self.resize(900, 700)
        self.setStyleSheet(f"background-color: {THEME_COLORS['background']};")
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked Widget for pages
        self.stack = QStackedWidget()
        
        self.dashboard = Dashboard()
        self.achievements = AchievementsPanel()
        self.profile = ProfilePanel()
        self.settings = SettingsPanel()
        
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.achievements)
        self.stack.addWidget(self.profile)
        self.stack.addWidget(self.settings)
        
        layout.addWidget(self.stack)
        
        # Navigation Bar
        nav_container = QWidget()
        nav_container.setStyleSheet(f"background-color: {THEME_COLORS['panel']}; border-top: 1px solid {THEME_COLORS['border']};")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        nav_layout.setAlignment(Qt.AlignCenter)
        
        self.nav_btns = []
        
        btn_dashboard = self.create_nav_btn("Dashboard", 0)
        btn_achievements = self.create_nav_btn("Achievements", 1)
        btn_profile = self.create_nav_btn("Profile", 2)
        btn_settings = self.create_nav_btn("Settings", 3)
        
        nav_layout.addWidget(btn_dashboard)
        nav_layout.addWidget(btn_achievements)
        nav_layout.addWidget(btn_profile)
        nav_layout.addWidget(btn_settings)
        
        layout.addWidget(nav_container)
        
        self.set_active_nav(0)
        
    def create_nav_btn(self, text, index):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(120, 36)
        btn.clicked.connect(lambda: self.switch_page(index))
        self.nav_btns.append(btn)
        return btn
        
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        self.set_active_nav(index)
        
        # Refresh data when switching
        if index == 0:
            self.dashboard.refresh_stats()
            self.dashboard.graph.refresh_data()
        elif index == 1:
            self.achievements.refresh_data()
        elif index == 2:
            self.profile.refresh_data()
            
    def set_active_nav(self, index):
        for i, btn in enumerate(self.nav_btns):
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {THEME_COLORS['border']};
                        color: {THEME_COLORS['text_primary']};
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {THEME_COLORS['text_secondary']};
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        color: {THEME_COLORS['text_primary']};
                    }}
                """)
