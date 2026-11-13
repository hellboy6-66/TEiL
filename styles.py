"""Стили (QSS) для тем оформления TEiL."""

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e; color: #cdd6f4;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace; font-size: 13px;
}
QLabel#cwdLabel { color: #89b4fa; font-weight: bold; padding: 4px 8px; background-color: #11111b; border-radius: 4px; }
QLabel#sectionTitle { color: #a6e3a1; font-weight: bold; padding: 4px 2px; }
QLabel#preview { color: #a6e3a1; background-color: #11111b; padding: 6px 8px; border-radius: 4px; font-family: "Consolas", monospace; }
QLineEdit { background-color: #11111b; border: 1px solid #313244; border-radius: 4px; padding: 5px 8px; color: #cdd6f4; }
QLineEdit:focus { border: 1px solid #89b4fa; }
QTextEdit#output { background-color: #11111b; border: 1px solid #313244; border-radius: 6px; padding: 8px; color: #a6e3a1; font-family: "Consolas", monospace; }
QTabWidget::pane { border: 1px solid #313244; border-radius: 6px; background: #181825; }
QPushButton#tabButton { background-color: #181825; color: #bac2de; border: 1px solid #313244; border-radius: 4px; padding: 6px 14px; font-weight: normal; min-height: 22px; text-align: center; }
QPushButton#tabButton:hover { background-color: #45475a; color: #cdd6f4; }
QPushButton#tabButton:checked { background-color: #313244; color: #89b4fa; border: 1px solid #89b4fa; }
QPushButton#cmdBtn { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 7px 10px; text-align: left; }
QPushButton#cmdBtn:hover { background-color: #45475a; border: 1px solid #89b4fa; }
QPushButton#cmdBtn:pressed { background-color: #585b70; }
QPushButton { background-color: #89b4fa; color: #11111b; border: none; border-radius: 4px; padding: 6px 14px; font-weight: bold; }
QPushButton:hover { background-color: #74a8f7; }
QPushButton:pressed { background-color: #5b93e6; }
QScrollArea { border: none; background: #181825; }
QScrollBar:vertical { background: #181825; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #181825; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #45475a; border-radius: 5px; min-width: 20px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QGroupBox { border: 1px solid #313244; border-radius: 4px; margin-top: 10px; padding: 8px 6px 6px 6px; color: #bac2de; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QCheckBox { color: #cdd6f4; padding: 2px; }
QCheckBox::indicator { width: 15px; height: 15px; }
QMessageBox, QDialog { background-color: #1e1e2e; }
QTextBrowser { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }
"""

LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f5f5f5; color: #333333;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace; font-size: 13px;
}
QLabel#cwdLabel { color: #005a9e; font-weight: bold; padding: 4px 8px; background-color: #e0e0e0; border-radius: 4px; }
QLabel#sectionTitle { color: #2e7d32; font-weight: bold; padding: 4px 2px; }
QLabel#preview { color: #2e7d32; background-color: #e8f5e9; padding: 6px 8px; border-radius: 4px; border: 1px solid #c8e6c9; font-family: "Consolas", monospace; }
QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 4px; padding: 5px 8px; color: #333333; }
QLineEdit:focus { border: 1px solid #005a9e; }
QTextEdit#output { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 6px; padding: 8px; color: #1b5e20; font-family: "Consolas", monospace; }
QTabWidget::pane { border: 1px solid #cccccc; border-radius: 6px; background: #ffffff; }
QPushButton#tabButton { background-color: #ffffff; color: #555555; border: 1px solid #cccccc; border-radius: 4px; padding: 6px 14px; font-weight: normal; min-height: 22px; text-align: center; }
QPushButton#tabButton:hover { background-color: #eeeeee; color: #000000; }
QPushButton#tabButton:checked { background-color: #e3f2fd; color: #005a9e; border: 1px solid #005a9e; }
QPushButton#cmdBtn { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; border-radius: 4px; padding: 7px 10px; text-align: left; }
QPushButton#cmdBtn:hover { background-color: #eeeeee; border: 1px solid #005a9e; }
QPushButton#cmdBtn:pressed { background-color: #dddddd; }
QPushButton { background-color: #005a9e; color: #ffffff; border: none; border-radius: 4px; padding: 6px 14px; font-weight: bold; }
QPushButton:hover { background-color: #004578; }
QPushButton:pressed { background-color: #003566; }
QScrollArea { border: none; background: #ffffff; }
QScrollBar:vertical { background: #f5f5f5; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #cccccc; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #aaaaaa; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #f5f5f5; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #cccccc; border-radius: 5px; min-width: 20px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 10px; padding: 8px 6px 6px 6px; color: #555555; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QCheckBox { color: #333333; padding: 2px; }
QCheckBox::indicator { width: 15px; height: 15px; }
QMessageBox, QDialog { background-color: #f5f5f5; }
QTextBrowser { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; border-radius: 6px; }
"""