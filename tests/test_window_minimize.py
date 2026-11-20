# -*- coding: utf-8 -*-
"""Run with Maya's mayapy; no Maya scene or standalone initialization required."""
import os
import sys
import unittest
from unittest.mock import Mock, patch

from PySide2.QtCore import QEventLoop, QPoint, QTimer, Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QApplication, QLineEdit, QWidget

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PoseDrive.gui.widget.widgetT import FramelessWindow


def process_events():
    loop = QEventLoop()
    QTimer.singleShot(80, loop.quit)
    loop.exec_()


class WindowMinimizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.host = QWidget()
        self.host.resize(1200, 800)
        self.host.show()
        self.content = QLineEdit("unsaved pose edit")
        self.window = FramelessWindow(self.content, self.host)
        self.window.setMinimumSize(1080, 720)
        self.window.resize(1120, 740)
        self.window.move(100, 100)
        self.window.show()
        process_events()

    def tearDown(self):
        self.window.close()
        self.host.close()
        self.window.deleteLater()
        self.host.deleteLater()
        process_events()

    def assert_compact_controls(self):
        self.assertTrue(self.window.isCompact())
        self.assertFalse(self.window.isMinimized())
        self.assertTrue(self.content.isHidden())
        self.assertEqual(int(self.window._edge_at(QPoint(0, 0))), 0)
        for button in (self.window.bar.min_button, self.window.bar.max_button,
                       self.window.bar.close_button):
            self.assertTrue(button.isVisible())
            bounds = button.rect().translated(button.mapTo(self.window, QPoint()))
            self.assertTrue(self.window.rect().contains(bounds))

    def test_minimize_restore_keeps_geometry_constraints_and_content(self):
        geometry = self.window.geometry()
        minimum, maximum = self.window.minimumSize(), self.window.maximumSize()
        constraint = self.window.main_layout.sizeConstraint()
        for unused in range(3):
            self.window.bar.min_button.click()
            process_events()
            self.assert_compact_controls()
            self.window.bar.max_button.click()
            process_events()
            self.assertFalse(self.window.isCompact())
            self.assertEqual(self.window.geometry(), geometry)
            self.assertEqual(self.window.minimumSize(), minimum)
            self.assertEqual(self.window.maximumSize(), maximum)
            self.assertEqual(self.window.main_layout.sizeConstraint(), constraint)
            self.assertTrue(self.content.isVisible())
            self.assertEqual(self.content.text(), "unsaved pose edit")

    def test_maximized_window_restores_maximized_then_normal_geometry(self):
        geometry = self.window.geometry()
        self.window.showMaximized()
        process_events()
        self.window.bar.min_button.click()
        process_events()
        self.assert_compact_controls()
        self.window.bar.max_button.click()
        process_events()
        self.assertTrue(self.window.isMaximized())
        self.window.bar.max_button.click()
        process_events()
        self.assertEqual(self.window.geometry(), geometry)

    def test_compact_minimize_button_restores_and_close_button_closes(self):
        self.window.bar.min_button.click()
        self.window.bar.min_button.click()
        process_events()
        self.assertFalse(self.window.isCompact())
        self.window.bar.min_button.click()
        process_events()
        self.window.bar.close_button.click()
        self.assertFalse(self.window.isVisible())

    def test_standalone_window_still_minimizes_natively(self):
        self.window.setParent(None, self.window.windowFlags())
        self.window.show()
        self.window.bar.min_button.click()
        process_events()
        self.assertTrue(self.window.isMinimized())
        self.assertFalse(self.window.isCompact())
        self.window.showNormal()

    def test_double_click_title_restores_compact_window(self):
        geometry = self.window.geometry()
        self.window.bar.min_button.click()
        process_events()
        QTest.mouseDClick(self.window.bar, Qt.LeftButton, pos=QPoint(130, 15))
        process_events()
        self.assertFalse(self.window.isCompact())
        self.assertEqual(self.window.geometry(), geometry)

    def test_compact_follows_host_when_tool_is_on_another_screen(self):
        screens = self.app.screens()
        if len(screens) < 2:
            self.skipTest("Requires two screens")
        for index, screen in enumerate(screens):
            with self.subTest(screen=screen.name()):
                self.host.move(screen.availableGeometry().topLeft() + QPoint(100, 100))
                other = screens[(index + 1) % len(screens)]
                self.window.move(other.availableGeometry().topLeft() + QPoint(100, 100))
                process_events()
                self.window.bar.min_button.click()
                process_events()
                expected = self.host.mapToGlobal(QPoint(
                    self.window.Margins,
                    self.host.height() - self.window.height() - self.window.Margins))
                self.assertEqual(self.window.pos(), expected)
                self.assertTrue(screen.availableGeometry().contains(self.window.geometry()))
                self.window.restoreWindow()
                process_events()

    def test_compact_uses_host_position_even_if_handle_reports_other_screen(self):
        screens = self.app.screens()
        if len(screens) < 2:
            self.skipTest("Requires two screens")
        self.host.move(screens[0].availableGeometry().topLeft() + QPoint(100, 100))
        process_events()
        stale_handle = Mock()
        stale_handle.screen.return_value = screens[1]
        with patch.object(self.host, "windowHandle", return_value=stale_handle):
            self.window.bar.min_button.click()
            process_events()
        expected = self.host.mapToGlobal(QPoint(
            self.window.Margins,
            self.host.height() - self.window.height() - self.window.Margins))
        self.assertEqual(self.window.pos(), expected)


if __name__ == "__main__":
    unittest.main()
