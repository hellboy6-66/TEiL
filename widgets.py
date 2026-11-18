"""Пользовательские виджеты для TEiL."""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal


class DragScrollArea(QScrollArea):
    """QScrollArea с прокруткой перетаскиванием мыши."""
    DRAG_THRESHOLD = 8
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._press_pos = None
        self._scroll_start = None
        self.viewport().installEventFilter(self)

    def setWidget(self, widget):
        super().setWidget(widget)
        self._install_filter_recursive(widget)

    def _install_filter_recursive(self, widget):
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()
        if et == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._scroll_start = (self.horizontalScrollBar().value(), self.verticalScrollBar().value())
            self._dragging = False
        elif et == QEvent.Type.MouseMove:
            if self._press_pos is not None:
                delta = event.globalPosition().toPoint() - self._press_pos
                if not self._dragging and delta.manhattanLength() > self.DRAG_THRESHOLD:
                    self._dragging = True
                    self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                if self._dragging:
                    self.horizontalScrollBar().setValue(self._scroll_start[0] - delta.x())
                    self.verticalScrollBar().setValue(self._scroll_start[1] - delta.y())
                    return True
        elif et == QEvent.Type.MouseButtonRelease:
            was_dragging = self._dragging
            self._press_pos = None
            self._dragging = False
            self.viewport().unsetCursor()
            if was_dragging: return True
        return super().eventFilter(obj, event)


class CategoryBar(QWidget):
    """Горизонтальная полоса категорий."""
    category_selected = pyqtSignal(int)
    
    def __init__(self, categories: list[str], parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        
        self.scroll = DragScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(2)
        
        self.buttons: list[QPushButton] = []
        for i, name in enumerate(categories):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setObjectName("tabButton")
            btn.clicked.connect(lambda _=False, idx=i: self._select(idx))
            self.buttons.append(btn)
            hl.addWidget(btn)
        hl.addStretch()
        
        self.scroll.setWidget(container)
        outer.addWidget(self.scroll)
        if self.buttons: self.buttons[0].setChecked(True)

    def _select(self, idx: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == idx)
        self.category_selected.emit(idx)