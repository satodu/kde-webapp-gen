"""Custom Oriental Brutalist Visual Decorations for KDE Webapp Manager.
Implements design system tokens and micro-decorations:
- Dot Matrix canvas backgrounds
- Vertical Katakana/Kanji architectural rulers (Concept 'Ma')
- Hanko Stamp seals (Electric Cobalt & Vermilion)
- Status pills and crosshair grid markers (+ + + +)
"""

from typing import Optional
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtGui import QPainter, QColor, QPen

class DotMatrixCanvas(QFrame):
    """Bento Card subclass with a custom 1px dot-matrix pattern background."""
    def __init__(self, parent: Optional[QWidget] = None, dot_spacing: int = 16, dot_color: str = "rgba(222, 223, 215, 0.05)") -> None:
        super().__init__(parent)
        self.dot_spacing = dot_spacing
        self.dot_color = QColor(dot_color) if dot_color.startswith("#") else QColor(222, 223, 215, 12)
        self.setProperty("class", "bentoCard")

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        pen = QPen(self.dot_color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        w = self.width()
        h = self.height()
        
        # Draw dot matrix grid inside margins
        margin = 12
        for x in range(margin, w - margin, self.dot_spacing):
            for y in range(margin, h - margin, self.dot_spacing):
                painter.drawPoint(QPointF(x, y))
        painter.end()


class VerticalKanjiRuler(QWidget):
    """Vertical architectural line with Katakana/Kanji text serving as a structural guide (Concept 'Ma')."""
    def __init__(self, text: str = "ウェブアプリ // 制御", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(22)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        # Character vertical stack
        for char in text:
            lbl = QLabel(char)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("""
                color: #4a525d;
                font-size: 10px;
                font-family: 'Noto Sans CJK JP', 'Kaku Gothic', 'Inter', monospace;
                font-weight: 700;
                background: transparent;
            """)
            layout.addWidget(lbl)
            
        layout.addStretch()


class HankoBadge(QLabel):
    """Oriental Stamp Badge (Hanko) in Cobalt Blue or Hanko Vermilion."""
    def __init__(self, text: str = "網", style_variant: str = "blue", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if style_variant == "vermilion":
            self.setStyleSheet("""
                background-color: rgba(230, 57, 70, 0.12);
                border: 1px solid #E63946;
                border-radius: 4px;
                color: #ff6b72;
                font-weight: 800;
                font-size: 11px;
                padding: 2px 6px;
                font-family: monospace;
            """)
        else: # Electric Cobalt default
            self.setStyleSheet("""
                background-color: rgba(37, 99, 235, 0.12);
                border: 1px solid #2563eb;
                border-radius: 4px;
                color: #60a5fa;
                font-weight: 800;
                font-size: 11px;
                padding: 2px 6px;
                font-family: monospace;
            """)


class TechnicalCrosshairs(QLabel):
    """Rhythmic crosshair pattern (+ + + +) indicator."""
    def __init__(self, count: int = 4, parent: Optional[QWidget] = None) -> None:
        text = " ".join(["+"] * count)
        super().__init__(text, parent)
        self.setObjectName("crosshairDecor")
        self.setStyleSheet("""
            color: rgba(222, 223, 215, 0.16);
            font-size: 11px;
            font-family: monospace;
            font-weight: 700;
            letter-spacing: 2px;
            background: transparent;
        """)


class StatusIndicatorPill(QWidget):
    """Translucent pill container with glowing status dot and monospace label."""
    def __init__(self, label: str = "SYSTEM.READY", active: bool = True, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 10, 3)
        layout.setSpacing(6)
        
        # Glowing dot indicator
        self.dot = QLabel("●" if active else "○")
        dot_color = "#3b82f6" if active else "#7e8790"
        self.dot.setStyleSheet(f"color: {dot_color}; font-size: 8px; background: transparent;")
        layout.addWidget(self.dot)
        
        # Text label
        self.lbl = QLabel(label)
        self.lbl.setStyleSheet("""
            color: #dedfd7;
            font-size: 10px;
            font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: transparent;
        """)
        layout.addWidget(self.lbl)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 23, 31, 0.80);
                border: 1px solid rgba(222, 223, 215, 0.08);
                border-radius: 12px;
            }
        """)
