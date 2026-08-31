import sys
from PySide6.QtWidgets import QApplication
from database.migrations import initialize_db
from ui.main_window import MainWindow

def main():
    # 1. Initialize database
    initialize_db()
    
    # 2. Launch Application
    app = QApplication(sys.argv)
    
    # Optional: Apply some global styling or palette here
    # Dark mode is standard on modern macOS, but we will style widgets directly.
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
