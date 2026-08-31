from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PySide6.QtCore import Qt, QRectF, QPointF, QSize, QEvent
from config import THEME_COLORS
from services.stats_service import get_contribution_data
from datetime import datetime, timedelta

class ContributionGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 150)
        self.data = []
        self.cell_size = 12
        self.cell_margin = 3
        self.setMouseTracking(True)
        self.refresh_data()
        
    def refresh_data(self):
        self.data = get_contribution_data(365)
        self.update()
        
    def get_color(self, level, color_list):
        if level < 0: level = 0
        if level >= len(color_list): level = len(color_list) - 1
        return QColor(color_list[level])
        
    def get_cell_rect(self, col, row):
        x = col * (self.cell_size + self.cell_margin)
        y = row * (self.cell_size + self.cell_margin)
        return QRectF(x, y, self.cell_size, self.cell_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            return
            
        # Align so the last day is today, and it sits at the rightmost column.
        # Today's weekday
        today_dt = datetime.strptime(self.data[-1]['date'], "%Y-%m-%d")
        today_row = today_dt.weekday() # 0 = Monday, 6 = Sunday
        
        # Calculate start column for drawing
        total_days = len(self.data)
        
        # We draw left to right.
        # The last cell goes in `today_row`.
        # So cell index `i` maps to some (col, row).
        # Let's map backwards from the end.
        
        painter.translate(20, 20) # padding
        
        for i, day in enumerate(reversed(self.data)):
            # `i` is days ago (0 = today)
            # Row mapping:
            row = (today_row - i) % 7
            # Col mapping (weeks ago):
            col = 52 - ((i + (6 - today_row)) // 7)
            
            if col < 0:
                continue
                
            rect = self.get_cell_rect(col, row)
            
            # Colors
            green_color = self.get_color(day['green_level'], THEME_COLORS['green_levels'])
            
            # Red color has alpha in config, let's parse it safely
            red_str = THEME_COLORS['red_levels'][day['red_level']]
            if red_str.startswith("rgba"):
                parts = red_str[5:-1].split(',')
                red_color = QColor(int(parts[0]), int(parts[1]), int(parts[2]), int(float(parts[3])*255))
            else:
                red_color = QColor(red_str)
                
            empty_color = QColor(THEME_COLORS['graph_empty'])
            
            # Draw cell
            painter.setPen(Qt.NoPen)
            
            if day['green_level'] > 0 and day['red_level'] > 0:
                # Diagonal split
                # Top-left triangle for green
                p1 = QPolygonF([
                    rect.topLeft(),
                    rect.topRight(),
                    rect.bottomLeft()
                ])
                painter.setBrush(green_color)
                painter.drawPolygon(p1)
                
                # Bottom-right triangle for red
                p2 = QPolygonF([
                    rect.topRight(),
                    rect.bottomRight(),
                    rect.bottomLeft()
                ])
                painter.setBrush(red_color)
                painter.drawPolygon(p2)
            elif day['green_level'] > 0:
                painter.setBrush(green_color)
                painter.drawRoundedRect(rect, 2, 2)
            elif day['red_level'] > 0:
                painter.setBrush(red_color)
                painter.drawRoundedRect(rect, 2, 2)
            else:
                painter.setBrush(empty_color)
                painter.drawRoundedRect(rect, 2, 2)
                
            # Draw border
            painter.setPen(QPen(QColor(THEME_COLORS['graph_outline']), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(rect, 2, 2)
            
            # Store rect in data for tooltips
            self.data[total_days - 1 - i]['rect'] = rect

    def event(self, event):
        if event.type() == QEvent.ToolTip:
            pos = event.pos()
            # translate pos due to padding
            adjusted_pos = QPointF(pos.x() - 20, pos.y() - 20)
            
            found = False
            for day in self.data:
                rect = day.get('rect')
                if rect and rect.contains(adjusted_pos):
                    # Format tooltip
                    dt = datetime.strptime(day['date'], "%Y-%m-%d").strftime("%B %d, %Y")
                    tasks = day['completed_tasks']
                    
                    secs = day['study_seconds']
                    hours, rem = divmod(secs, 3600)
                    mins, _ = divmod(rem, 60)
                    study_str = f"{int(hours)}h {int(mins)}m" if hours > 0 else f"{int(mins)}m"
                    if secs == 0: study_str = "0m"
                    
                    if tasks == 0 and secs == 0:
                        text = f"{dt}\n\nNo activity"
                    else:
                        text = f"{dt}\n\n{tasks} tasks completed\n{study_str} studied"
                        if day['is_green_day']: text += "\nGreen Day ✓"
                        if day['is_red_day']: text += "\nRed Day ✓"
                        
                    QToolTip.showText(event.globalPos(), text, self)
                    found = True
                    break
            
            if not found:
                QToolTip.hideText()
            return True
            
        return super().event(event)
