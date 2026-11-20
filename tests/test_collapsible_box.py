# -*- coding: utf-8 -*-
"""Run with Maya's mayapy. Exercises real Qt widgets without opening a scene."""
import os
import sys
import unittest

from PySide2.QtCore import QEventLoop, QPoint, QTimer, Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QApplication, QVBoxLayout, QWidget

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PoseDrive.gui.widget.widgetT import _CollapsibleBox, _EButtonGroup, _JPlistWidget


def wait(ms=100):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


def rows(count):
    return [("pose_%d" % i, "Pose %d" % i, None) for i in range(count)]


class CollapsibleBoxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.host = QWidget()
        self.host.resize(320, 400)
        self.layout = QVBoxLayout(self.host)
        self.layout.setAlignment(Qt.AlignTop)
        self.box = _CollapsibleBox("Joint", animation_duration=40)
        self.layout.addWidget(self.box)
        self.host.show()
        wait(30)

    def tearDown(self):
        self.host.close()
        self.host.deleteLater()
        wait(30)

    def assert_rows_fit(self, count):
        expected = count * 25 + max(0, count - 1) * 2
        self.assertEqual(self.box.item_layout.count(), count)
        self.assertEqual(self.box.content_area.height(), expected)
        self.assertEqual(self.box.height(), self.box.toggle_button.height() + expected)
        for i in range(count):
            row = self.box.item_layout.itemAt(i).widget()
            bounds = row.rect().translated(row.mapTo(self.box.content_area, QPoint()))
            self.assertTrue(self.box.content_area.rect().contains(bounds))

    def test_first_update_after_show_and_direct_add(self):
        self.box.updateItems(rows(2))
        QTest.mouseDClick(self.box.toggle_button, Qt.LeftButton)
        wait()
        self.assertTrue(self.box.isExpanded())
        self.assert_rows_fit(2)
        self.box.addItem("third", "Third")
        wait()
        self.assert_rows_fit(3)

    def test_empty_double_click_then_add(self):
        QTest.mouseDClick(self.box.toggle_button, Qt.LeftButton)
        self.assertTrue(self.box.isExpanded())
        self.box.addItem("first", "First")
        wait()
        self.assert_rows_fit(1)

    def test_expanded_refresh_grows_shrinks_and_clears(self):
        self.box.setExpanded(True)
        self.box.toggle_button.setChecked(True)
        for count in (2, 8, 1, 0, 3):
            with self.subTest(count=count):
                self.box.updateItems(rows(count))
                self.assertEqual(self.box.item_layout.count(), count)
                wait()
                self.assert_rows_fit(count)
                self.assertTrue(self.box.isExpanded())
                self.assertTrue(self.box.toggle_button.isChecked())

    def test_clear_removes_rows_immediately_and_add_keeps_state(self):
        self.box.updateItems(rows(3))
        self.box.setExpanded(True, animate=False)
        self.box.clearItems()
        self.assertEqual(self.box.item_layout.count(), 0)
        self.box.addItem("replacement", "Replacement")
        wait()
        self.assert_rows_fit(1)

    def test_collapsed_refresh_stays_closed_until_double_click(self):
        self.box.updateItems(rows(2))
        self.box.updateItems(rows(6))
        wait()
        self.assertFalse(self.box.isExpanded())
        self.assertEqual(self.box.content_area.height(), 0)
        QTest.mouseDClick(self.box.toggle_button, Qt.LeftButton)
        wait()
        self.assert_rows_fit(6)

    def test_animation_reverse_and_update_continue_from_current_height(self):
        self.box.animation_duration = 180
        self.box.updateItems(rows(8))
        self.box.setExpanded(True)
        wait(65)
        height = self.box.content_area.height()
        self.assertGreater(height, 0)
        self.assertLess(height, 214)
        self.box.setExpanded(False)
        self.assertEqual(self.box.content_area.height(), height)
        wait(30)
        height = self.box.content_area.height()
        self.box.updateItems(rows(3))
        self.box.setExpanded(True)
        self.assertEqual(self.box.content_area.height(), height)
        wait(240)
        self.assert_rows_fit(3)

    def test_click_signal_keeps_pose_key_after_refresh(self):
        clicked = []
        self.box.item_clicked.connect(lambda key: clicked.append(key))
        self.box.updateItems(rows(3))
        self.box.updateItems([("replacement", "Visible name", None)])
        self.box.setExpanded(True, animate=False)
        wait(30)
        row = self.box.item_layout.itemAt(0).widget()
        QTest.mouseClick(row, Qt.LeftButton, pos=QPoint(row.width() - 5, 12))
        self.assertEqual(clicked, ["replacement"])

    def test_selection_is_independent_from_expansion(self):
        other = _CollapsibleBox("Other")
        self.layout.addWidget(other)
        group = _EButtonGroup(self.host)
        group.addButton(self.box.toggle_button)
        group.addButton(other.toggle_button)
        self.box.updateItems(rows(1))
        self.box.toggle_button.click()
        self.assertFalse(self.box.isExpanded())
        self.box.setExpanded(True, animate=False)
        other.toggle_button.click()
        self.assertFalse(self.box.toggle_button.isChecked())
        self.assertTrue(self.box.isExpanded())

    def test_list_rebuild_then_child_update_in_same_callback(self):
        listing = _JPlistWidget(self.host)
        self.layout.addWidget(listing)
        listing.updateItems([("joint", "joint", None)])
        listing.updateChildItems("joint", rows(2))
        listing.updateItems([("joint", "joint", None)])
        listing.updateChildItems("joint", rows(3))
        wait()
        box = listing.main_layout.itemAt(0).widget()
        self.assertEqual(listing.main_layout.count(), 1)
        self.assertEqual(box.item_layout.count(), 3)

    def test_many_rows_use_outer_scroll_and_follow_width(self):
        listing = _JPlistWidget(self.host)
        listing.setFixedHeight(220)
        self.layout.addWidget(listing)
        listing.updateItems([("joint", "joint", None)])
        listing.updateChildItems("joint", rows(30))
        box = listing.main_layout.itemAt(0).widget()
        box.setExpanded(True, animate=False)
        wait()
        self.assertGreater(listing.verticalScrollBar().maximum(), 0)
        last_row = box.item_layout.itemAt(29).widget()
        listing.ensureWidgetVisible(last_row)
        wait(30)
        self.assertTrue(listing.viewport().rect().contains(
            last_row.mapTo(listing.viewport(), last_row.rect().center())))
        self.host.resize(450, 400)
        wait(30)
        self.assertEqual(box.content_widget.width(), box.content_area.width())

    def test_add_joint_keeps_existing_poses_and_double_click(self):
        listing = _JPlistWidget(self.host)
        self.layout.addWidget(listing)
        listing.updateItems([("joint", "joint", None)])
        listing.updateChildItems("joint", rows(2))
        wait(30)
        # Matches BodyWidget.addJointAndPose: update joints without repopulating poses.
        listing.updateItems([("joint", "joint", None), ("new", "new", None)])
        wait(30)
        box = listing.main_layout.itemAt(0).widget()
        self.assertEqual(box.item_layout.count(), 2)
        box.animation_duration = 0
        QTest.mouseDClick(box.toggle_button, Qt.LeftButton)
        wait(30)
        self.assertTrue(box.isExpanded())
        self.assertEqual(box.content_area.height(), 52)
        QTest.mouseDClick(box.toggle_button, Qt.LeftButton)
        wait(30)
        self.assertFalse(box.isExpanded())
        self.assertEqual(box.content_area.height(), 0)

    def test_joint_refresh_preserves_identity_state_and_signal_connections(self):
        listing = _JPlistWidget(self.host)
        self.layout.addWidget(listing)
        listing.updateItems([("a", "Same name", None), ("b", "Same name", None)])
        listing.updateChildItems("a", rows(2))
        listing.updateChildItems("b", rows(1))
        first = listing.main_layout.itemAt(0).widget()
        second = listing.main_layout.itemAt(1).widget()
        first.setExpanded(True, animate=False)
        first.toggle_button.click()
        clicked = []
        listing.item_clicked.connect(lambda keys: clicked.append(keys))
        for unused in range(3):
            listing.updateItems([("b", "Same name", None), ("a", "Renamed", None),
                                 ("c", "New", None)])
        wait(30)
        self.assertIs(listing.main_layout.itemAt(0).widget(), second)
        self.assertIs(listing.main_layout.itemAt(1).widget(), first)
        self.assertTrue(first.isExpanded())
        self.assertTrue(first.toggle_button.isChecked())
        self.assertIs(listing.button_group.current_checked_button, first.toggle_button)
        self.assertEqual(first.content_area.height(), 52)
        self.assertEqual(second.item_layout.count(), 1)
        self.assertEqual(len(listing.button_group.buttons()), 3)
        listing.updateChildItems("a", [("pose_new", "New pose", None)])
        wait(350)
        row = first.item_layout.itemAt(0).widget()
        QTest.mouseClick(row, Qt.LeftButton, pos=QPoint(row.width() - 5, 12))
        self.assertEqual(clicked, [["a", "pose_new"]])

    def test_joint_remove_clear_and_readd_do_not_reuse_deleted_panels(self):
        listing = _JPlistWidget(self.host)
        self.layout.addWidget(listing)
        first = listing.addJointItem("a", "A")
        listing.addJointItem("a", "Renamed A")
        self.assertEqual(listing.main_layout.count(), 1)
        listing.addJointItem("b", "B")
        first.toggle_button.click()
        listing.updateItems([("b", "B", None)])
        self.assertIsNone(listing.button_group.current_checked_button)
        self.assertEqual(len(listing.button_group.buttons()), 1)
        listing.updateItems([("a", "A", None), ("b", "B", None)])
        replacement = listing.main_layout.itemAt(0).widget()
        self.assertIsNot(replacement, first)
        self.assertEqual(replacement.item_layout.count(), 0)
        listing.clearItems()
        listing.addJointItem("a", "A")
        listing.updateChildItems("a", rows(2))
        self.assertEqual(listing.main_layout.count(), 1)
        self.assertEqual(listing.main_layout.itemAt(0).widget().item_layout.count(), 2)


if __name__ == "__main__":
    unittest.main()
