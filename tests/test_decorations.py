import unittest
from PyQt6.QtWidgets import QApplication
from webapp_manager.widgets.decorations import (
    DotMatrixCanvas, VerticalKanjiRuler, HankoBadge, TechnicalCrosshairs, StatusIndicatorPill
)

app = QApplication.instance()
if not app:
    app = QApplication([])

class TestDecorations(unittest.TestCase):
    def test_hanko_badge_creation(self):
        hanko_blue = HankoBadge("網", style_variant="blue")
        hanko_red = HankoBadge("規", style_variant="vermilion")
        self.assertEqual(hanko_blue.text(), "網")
        self.assertEqual(hanko_red.text(), "規")

    def test_technical_crosshairs(self):
        cross = TechnicalCrosshairs(count=4)
        self.assertEqual(cross.text(), "+ + + +")

    def test_status_indicator_pill(self):
        pill_active = StatusIndicatorPill("SYS.READY", active=True)
        pill_inactive = StatusIndicatorPill("SYS.OFFLINE", active=False)
        self.assertEqual(pill_active.lbl.text(), "SYS.READY")
        self.assertEqual(pill_active.dot.text(), "●")
        self.assertEqual(pill_inactive.dot.text(), "○")

    def test_dot_matrix_canvas_instantiation(self):
        canvas = DotMatrixCanvas(dot_spacing=16, dot_color="#2563eb")
        self.assertEqual(canvas.dot_spacing, 16)
        canvas.resize(200, 200)

    def test_vertical_kanji_ruler(self):
        ruler = VerticalKanjiRuler("管理")
        self.assertIsNotNone(ruler)
