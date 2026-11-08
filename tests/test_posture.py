from pathlib import Path
import shutil
import tempfile
from time import monotonic
import unittest
from uuid import uuid4

from PySide6.QtCore import QEvent, QPointF, QSettings, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from pomodoro.app import Companion


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


class PostureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.folder = Path(tempfile.gettempdir()) / f"pomodoro-posture-{uuid4().hex}"
        self.folder.mkdir()
        self.clock, self.pose_clock = Clock(), Clock()
        self.store = QSettings(str(self.folder / "settings.ini"), QSettings.Format.IniFormat)
        self.owner = Companion(self.app, self.store, self.clock, show_tray=False, pose_clock=self.pose_clock)
        self.owner.set_effects(False)
        self.owner.set_work(1)
        self.owner.set_rest(1)
        self.pet = self.owner.pet
        self.pet.next_idle = float("inf")
        self.pet.hovered = False
        area = self.app.primaryScreen().availableGeometry()
        self.pet.place_at(QPointF(area.center().x() - 72, area.bottom() - self.pet.height() + 1))

    def tearDown(self):
        self.owner.shutdown()
        self.app.aboutToQuit.disconnect(self.owner.shutdown)
        self.app.processEvents()
        self.assertEqual(self.folder.resolve().parent, Path(tempfile.gettempdir()).resolve())
        shutil.rmtree(self.folder)

    def break_start(self):
        self.owner.toggle()
        self.clock.now = 60
        self.owner.tick()
        self.assertEqual(self.owner.timer.phase, "break")

    def step_pose(self, now):
        self.pose_clock.now = now
        self.pet.last_tick = monotonic() - .08
        self.pet.tick()

    def test_rest_sits_in_place_and_blocks_walk_idle_and_hop_without_pinning(self):
        anchor = self.pet.pos()
        self.break_start()
        self.assertEqual(self.pet.posture.state, "sitting_down")
        self.step_pose(.3)
        self.assertTrue(0 < self.pet.posture.amount < 1)
        self.assertEqual(self.pet.pos(), anchor)
        self.step_pose(.7)
        self.assertEqual(self.pet.posture.state, "seated")
        self.pet.next_idle = -1
        self.assertFalse(self.pet.react("hop"))
        self.step_pose(8)
        self.assertEqual(self.pet.pos(), anchor)
        self.assertIsNone(self.pet.reaction)
        self.assertTrue(self.pet.resting)
        self.assertFalse(self.pet.pinned)
        self.assertTrue(self.owner.walking)
        self.assertTrue(self.store.value("walking", True, type=bool))
        self.assertFalse(self.store.contains("position"))

    def test_waiting_stays_seated_then_stands_before_resuming_walk(self):
        self.break_start()
        self.step_pose(.7)
        anchor = self.pet.pos()
        self.clock.now = 120
        self.owner.tick()
        self.assertEqual(self.owner.timer.phase, "waiting")
        self.assertEqual(self.pet.posture.state, "seated")
        self.assertFalse(self.pet.resting)
        self.owner.toggle()
        self.assertEqual(self.pet.posture.state, "standing_up")
        self.step_pose(1.0)
        self.assertEqual(self.pet.pos(), anchor)
        self.assertGreater(self.pet.posture.amount, 0)
        self.step_pose(1.5)
        self.assertEqual(self.pet.posture.state, "standing")
        self.assertNotEqual(self.pet.pos().x(), anchor.x())

    def test_paused_break_and_walking_option_do_not_wake_the_pet(self):
        self.break_start()
        self.step_pose(.7)
        self.owner.toggle()
        self.assertTrue(self.owner.timer.paused)
        self.owner.set_walking(False)
        self.owner.set_walking(True)
        anchor = self.pet.pos()
        self.step_pose(20)
        self.assertEqual(self.pet.pos(), anchor)
        self.assertEqual(self.pet.posture.state, "seated")
        self.assertTrue(self.pet.resting)

    def test_pinned_preference_survives_rest_and_standing(self):
        self.owner.set_walking(False)
        self.break_start()
        self.step_pose(.7)
        anchor = self.pet.pos()
        self.clock.now = 120
        self.owner.tick()
        self.owner.toggle()
        self.step_pose(1.5)
        self.assertEqual(self.pet.posture.state, "standing")
        self.assertEqual(self.pet.pos(), anchor)
        self.assertTrue(self.pet.pinned)
        self.assertFalse(self.owner.walking)

    def test_reset_cancels_sitting_and_recovery_keeps_break_posture(self):
        self.break_start()
        self.step_pose(.25)
        self.owner.recover_pet()
        self.assertEqual(self.pet.posture.phase, "break")
        self.step_pose(.7)
        self.assertEqual(self.pet.posture.state, "seated")
        self.owner.reset()
        self.assertEqual(self.pet.posture.state, "standing_up")
        self.step_pose(1.5)
        self.assertEqual(self.pet.posture.state, "standing")
        self.step_pose(4)
        self.assertEqual(self.pet.posture.phase, "ready")

    def test_rapid_phase_reversal_stays_continuous_without_stale_movement(self):
        anchor = self.pet.pos()
        self.break_start()
        self.step_pose(.3)
        mid = self.pet.posture.amount
        self.owner.reset()
        self.assertAlmostEqual(self.pet.posture.amount, mid)
        self.owner.toggle()
        self.clock.now += 60
        self.owner.tick()
        self.assertAlmostEqual(self.pet.posture.amount, mid)
        self.step_pose(.5)
        self.assertGreater(self.pet.posture.amount, mid)
        self.assertEqual(self.pet.pos(), anchor)
        self.step_pose(1.5)
        self.assertEqual(self.pet.posture.state, "seated")
        self.assertEqual(self.pet.pos(), anchor)

    def test_dragging_while_seated_remains_available_and_saves_pinning(self):
        self.break_start()
        self.step_pose(.7)
        anchor = QPointF(self.pet.pos())
        local = QPointF(70, 90)
        start, end = anchor + local, anchor + local + QPointF(80, -30)
        def event(kind, global_pos, button, buttons):
            return QMouseEvent(kind, local, global_pos, button, buttons, Qt.KeyboardModifier.NoModifier)
        self.pet.mousePressEvent(event(QEvent.Type.MouseButtonPress, start, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton))
        self.pet.mouseMoveEvent(event(QEvent.Type.MouseMove, end, Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton))
        self.pet.mouseReleaseEvent(event(QEvent.Type.MouseButtonRelease, end, Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton))
        moved = self.pet.pos()
        self.assertNotEqual(QPointF(moved), anchor)
        self.assertTrue(self.pet.pinned)
        self.assertFalse(self.owner.walking)
        self.assertTrue(self.pet.resting)
        self.assertFalse(self.pet.pointer_active)
        self.assertEqual(self.store.value("position"), moved)
        self.step_pose(5)
        self.assertEqual(self.pet.pos(), moved)
