import shutil
import json
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFrame, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from config import THEME_COLORS, DB_PATH
from database.db import get_connection

class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignTop)
        
        header = QLabel("SETTINGS")
        header.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 24px;")
        layout.addWidget(header)
        layout.addSpacing(20)
        
        self.add_section_title(layout, "Data Management")
        
        # Database Location
        loc_label = QLabel(f"Database Location: {DB_PATH}")
        loc_label.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(loc_label)
        layout.addSpacing(10)
        
        # Export Button
        export_btn = self.create_btn("Export Data (JSON)")
        export_btn.clicked.connect(self.export_data)
        layout.addWidget(export_btn)
        
        # Import Button
        import_btn = self.create_btn("Import Data (JSON)")
        import_btn.clicked.connect(self.import_data)
        layout.addWidget(import_btn)
        
        # Reset Button
        layout.addSpacing(20)
        reset_btn = self.create_btn("Reset Application Data", danger=True)
        reset_btn.clicked.connect(self.reset_data)
        layout.addWidget(reset_btn)
        
    def add_section_title(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-weight: bold; font-size: 16px;")
        layout.addWidget(lbl)
        
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background-color: {THEME_COLORS['border']};")
        layout.addWidget(div)
        
    def create_btn(self, text, danger=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(200, 36)
        
        bg = "#6E1414" if danger else THEME_COLORS['border']
        hover = "#8E1A1A" if danger else THEME_COLORS['text_secondary']
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {THEME_COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)
        return btn
        
    def export_data(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "JSON Files (*.json)")
        if not filepath:
            return
            
        try:
            data = {}
            with get_connection() as conn:
                for table in ['tasks', 'task_completions', 'study_sessions', 'user_achievements']:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table}")
                    data[table] = [dict(row) for row in cursor.fetchall()]
                    
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
                
            QMessageBox.information(self, "Success", "Data exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
            
    def import_data(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Data", "", "JSON Files (*.json)")
        if not filepath:
            return
            
        reply = QMessageBox.question(self, "Confirm Import", 
                                     "Importing will replace your current data. Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            with get_connection() as conn:
                cursor = conn.cursor()
                for table in ['tasks', 'task_completions', 'study_sessions', 'user_achievements']:
                    cursor.execute(f"DELETE FROM {table}")
                    if table in data and data[table]:
                        columns = data[table][0].keys()
                        placeholders = ",".join(["?"] * len(columns))
                        cols_str = ",".join(columns)
                        query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
                        for row in data[table]:
                            cursor.execute(query, tuple(row[col] for col in columns))
                conn.commit()
                
            QMessageBox.information(self, "Success", "Data imported successfully. Please restart the app.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
            
    def reset_data(self):
        reply = QMessageBox.question(self, "Confirm Reset", 
                                     "This will permanently delete all data. Are you absolutely sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
            
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                for table in ['tasks', 'task_completions', 'study_sessions', 'user_achievements']:
                    cursor.execute(f"DELETE FROM {table}")
                conn.commit()
            QMessageBox.information(self, "Success", "Application data has been reset.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset: {str(e)}")
