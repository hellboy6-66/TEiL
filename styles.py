"""Стили (QSS) для тем оформления TEiL."""

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e; color: #cdd6f4;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace; font-size: 13px;
}
QLabel#cwdLabel { color: #89b4fa; font-weight: bold; padding: 4px 8px; background-color: #11111b; border-radius: 4px; }
QLabel#sectionTitle { color: #a6e3a1; font-weight: bold; padding: 4px 2px; }
QLabel#preview { color: #a6e3a1; background-color: #11111b; padding: 6px 8px; border-radius: 4px; font-family: "Consolas", monospace; }

QLineEdit, QSpinBox { background-color: #11111b; border: 1px solid #313244; border-radius: 4px; padding: 5px 8px; color: #cdd6f4; }
QLineEdit:focus, QSpinBox:focus { border: 1px solid #89b4fa; }
QSpinBox::up-button, QSpinBox::down-button { background-color: #313244; width: 16px; border-radius: 2px; }
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #45475a; }

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

/* Стили для ползунка (История команд) */
QSlider::groove:horizontal { border: 1px solid #313244; height: 6px; background: #11111b; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #89b4fa; border-radius: 3px; }
QSlider::handle:horizontal { background: #cdd6f4; border: 2px solid #89b4fa; width: 14px; height: 14px; margin: -5px 0; border-radius: 8px; }

/* Стили для Дерева файлов (Проводник) */
QTreeView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    outline: none;
    padding: 5px;
}
QTreeView::item { padding: 4px; border-radius: 4px; }
QTreeView::item:hover { background-color: #313244; }
QTreeView::item:selected { background-color: #89b4fa; color: #11111b; }
QHeaderView::section {
    background-color: #11111b;
    color: #cdd6f4;
    border: none;
    padding: 4px;
    border-bottom: 1px solid #313244;
}

/* Стили для выпадающего списка подсказок (QCompleter) */
QListView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    outline: none;
}
QListView::item { padding: 4px; }
QListView::item:selected { background-color: #89b4fa; color: #11111b; }
"""

LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f5f5f5; color: #333333;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace; font-size: 13px;
}
QLabel#cwdLabel { color: #005a9e; font-weight: bold; padding: 4px 8px; background-color: #e0e0e0; border-radius: 4px; }
QLabel#sectionTitle { color: #2e7d32; font-weight: bold; padding: 4px 2px; }
QLabel#preview { color: #2e7d32; background-color: #e8f5e9; padding: 6px 8px; border-radius: 4px; border: 1px solid #c8e6c9; font-family: "Consolas", monospace; }

QLineEdit, QSpinBox { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 4px; padding: 5px 8px; color: #333333; }
QLineEdit:focus, QSpinBox:focus { border: 1px solid #005a9e; }
QSpinBox::up-button, QSpinBox::down-button { background-color: #e0e0e0; width: 16px; border-radius: 2px; }
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #cccccc; }

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

/* Стили для ползунка (История команд) */
QSlider::groove:horizontal { border: 1px solid #cccccc; height: 6px; background: #f0f0f0; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #005a9e; border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; border: 2px solid #005a9e; width: 14px; height: 14px; margin: -5px 0; border-radius: 8px; }

/* Стили для Дерева файлов (Проводник) */
QTreeView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 6px;
    outline: none;
    padding: 5px;
}
QTreeView::item { padding: 4px; border-radius: 4px; }
QTreeView::item:hover { background-color: #e0e0e0; }
QTreeView::item:selected { background-color: #005a9e; color: #ffffff; }
QHeaderView::section {
    background-color: #f5f5f5;
    color: #333333;
    border: none;
    padding: 4px;
    border-bottom: 1px solid #cccccc;
}

/* Стили для выпадающего списка подсказок (QCompleter) */
QListView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    outline: none;
}
QListView::item { padding: 4px; }
QListView::item:selected { background-color: #005a9e; color: #ffffff; }
"""