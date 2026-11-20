# -*- coding: utf-8 -*-
"""UI interaction regressions using test_ui's manual data objects, without Maya."""
import os
import sys
import unittest

from PySide2.QtCore import Qt, QEventLoop, QTimer
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from PoseDrive.test_ui import TestJointProtocol, TestPoseProtocol
from PoseDrive.gui.preview_data import JointPosePreviewData
from PoseDrive.gui.ui import BodyWidget


def wait(ms=40):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


class PreviewUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = JointPosePreviewData(TestJointProtocol, TestPoseProtocol)
        self.a = self.data.addJoint(TestJointProtocol())
        self.b = self.data.addJoint(TestJointProtocol())
        self.pose_a = self.data.addPose(self.a, TestPoseProtocol())
        self.data.addPose(self.a, TestPoseProtocol())
        self.body = BodyWidget(data=self.data)
        self.body.resize(900, 600)
        self.body.show()
        self.left = self.body.left_widget
        self.listing = self.left.jplist_widget
        wait()

    def tearDown(self):
        self.body.close()
        self.body.deleteLater()
        wait()

    def test_top_add_always_adds_collection_and_preserves_existing_panel(self):
        box = self.listing._items_by_key[self.a]
        box.setExpanded(True, animate=False)
        self.left.setSelection(self.a, self.pose_a)
        self.left._add_button.click()
        self.assertEqual(len(self.data.joints), 3)
        self.assertIs(self.listing._items_by_key[self.a], box)
        self.assertEqual(box.item_layout.count(), 2)
        self.assertTrue(box.isExpanded())
        self.assertEqual(len(self.data.joints[self.a]['poses']), 2)
        new_key = self.left._now_joint_key
        self.assertNotIn(new_key, (self.a, self.b))
        self.assertEqual(self.listing._items_by_key[new_key].item_layout.count(), 0)
        box.animation_duration = 0
        QTest.mouseDClick(box.toggle_button, Qt.LeftButton)
        self.assertFalse(box.isExpanded())
        QTest.mouseDClick(box.toggle_button, Qt.LeftButton)
        self.assertTrue(box.isExpanded())

    def test_add_pose_only_affects_target_after_adding_collections(self):
        for unused in range(3):
            self.left._add_button.click()
        box = self.listing._items_by_key[self.b]
        box.add_pose_button.click()
        self.assertEqual(len(self.data.joints[self.b]['poses']), 1)
        self.assertEqual(box.item_layout.count(), 1)
        self.assertEqual(len(self.data.joints[self.a]['poses']), 2)
        self.assertEqual(self.listing._items_by_key[self.a].item_layout.count(), 2)
        self.assertTrue(box.isExpanded())
        self.assertEqual(self.left._now_joint_key, self.b)
        selected = self.left._now_joint_child_key
        self.assertTrue(box._pose_rows[selected]._selected)
        self.assertEqual(self.body.right_widget.main_layout.count(), 1)

    def test_switching_collection_clears_pose_selection_before_delete(self):
        self.left.setSelection(self.a, self.pose_a)
        self.listing._items_by_key[self.b].toggle_button.click()
        self.assertEqual(self.left._now_joint_key, self.b)
        self.assertIsNone(self.left._now_joint_child_key)
        self.left._delete_button.click()
        self.assertNotIn(self.b, self.data.joints)
        self.assertIn(self.pose_a, self.data.joints[self.a]['poses'])
        self.assertIsNone(self.left._now_joint_key)
        self.assertFalse(self.left._delete_button.isEnabled())

    def test_delete_pose_refresh_and_reopen_keep_ownership(self):
        self.listing._items_by_key[self.b].add_pose_button.click()
        self.left._delete_button.click()
        self.assertEqual(self.data.joints[self.b]['poses'], {})
        self.assertEqual(len(self.data.joints[self.a]['poses']), 2)
        self.assertEqual(self.left._now_joint_key, self.b)
        self.assertIsNone(self.left._now_joint_child_key)
        self.body.refreshCollections()
        other = BodyWidget(data=self.data)
        try:
            self.assertEqual(other.left_widget.jplist_widget._items_by_key[self.a].item_layout.count(), 2)
            self.assertEqual(other.left_widget.jplist_widget._items_by_key[self.b].item_layout.count(), 0)
        finally:
            other.close()
            other.deleteLater()

    def test_rename_and_duplicate_names_do_not_change_identity(self):
        for key in (self.a, self.b):
            self.data.joints[key]['item']._name = 'Same name'
        self.body.refreshCollections()
        self.listing._items_by_key[self.b].add_pose_button.click()
        self.assertEqual(len(self.data.joints[self.a]['poses']), 2)
        self.assertEqual(len(self.data.joints[self.b]['poses']), 1)

    def test_empty_data_and_repeated_setup(self):
        self.data.joints.clear()
        self.body.refreshCollections()
        self.assertEqual(self.listing.main_layout.count(), 0)
        self.assertFalse(self.left._delete_button.isEnabled())
        self.left.addJointPoseList()
        self.left._add_button.click()
        self.assertEqual(len(self.data.joints), 1)
        self.assertEqual(self.listing.main_layout.count(), 1)


if __name__ == '__main__':
    unittest.main()
