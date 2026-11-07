import ctypes
import os
from pathlib import Path
import sys
import tempfile
import unittest
from uuid import uuid4

from PySide6.QtCore import QEvent, QPoint, QPointF, QSettings, Qt
from PySide6.QtGui import QContextMenuEvent, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from pomodoro.app import Companion
from pomodoro.text import TEXT
from pomodoro.timer import PomodoroTimer


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


class TimerTests(unittest.TestCase):
    def test_fractional_clock_does_not_add_a_second_at_start(self):
        clock = Clock()
        clock.now = 3606.5833333333426
        timer = PomodoroTimer(clock=clock)
        timer.toggle()
        self.assertEqual(timer.seconds, 3000)
        timer.toggle()
        self.assertEqual(timer.seconds, 3000)

    def test_default_cycle_waits_for_manual_start(self):
        clock = Clock()
        timer = PomodoroTimer(clock=clock)
        self.assertEqual((timer.phase, timer.seconds), ("ready", 3000))
        self.assertEqual(timer.toggle(), "work")
        clock.now = 2999.1
        self.assertIsNone(timer.advance())
        self.assertEqual(timer.seconds, 1)
        clock.now = 3000
        self.assertEqual(timer.advance(), "break")
        self.assertEqual(timer.seconds, 600)
        clock.now = 3600
        self.assertEqual(timer.advance(), "waiting")
        clock.now = 7200
        self.assertIsNone(timer.advance())
        self.assertEqual(timer.phase, "waiting")
        self.assertEqual(timer.toggle(), "work")

    def test_pause_resume_and_new_duration(self):
        clock = Clock()
        timer = PomodoroTimer(work=2, rest=1, clock=clock)
        timer.toggle()
        clock.now = 30.25
        timer.toggle()
        timer.work = 4
        timer.rest = 3
        clock.now = 1000
        self.assertIsNone(timer.advance())
        self.assertTrue(timer.paused)
        self.assertEqual(timer.seconds, 90)
        self.assertIsNone(timer.toggle())
        clock.now += 89.5
        self.assertIsNone(timer.advance())
        clock.now += .25
        self.assertEqual(timer.advance(), "break")
        self.assertEqual(timer.seconds, 180)
        timer.reset()
        self.assertEqual((timer.phase, timer.seconds), ("ready", 240))

    def test_click_at_boundary_does_not_pause_the_new_phase(self):
        clock = Clock()
        timer = PomodoroTimer(work=1, rest=1, clock=clock)
        timer.toggle()
        clock.now = 60
        self.assertEqual(timer.toggle(), "break")
        self.assertFalse(timer.paused)
        clock.now = 120
        self.assertEqual(timer.toggle(), "waiting")


class CompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def test_localized_menus_timer_effects_and_persistence(self):
        self.assertEqual(TEXT["en"].keys(), TEXT["ko"].keys())
        folder = Path(tempfile.gettempdir()) / f"pomodoro-test-{uuid4().hex}"
        folder.mkdir()
        path = folder / "pomodoro.ini"
        self.addCleanup(folder.rmdir)
        self.addCleanup(path.unlink, missing_ok=True)
        store = QSettings(str(path), QSettings.Format.IniFormat)
        store.setValue("rest", "invalid")
        clock = Clock()
        owner = Companion(self.app, store, clock, show_tray=False)
        try:
            self.exercise_companion(owner, clock, path)
        finally:
            if owner.options:
                owner.options.close()
            owner.shutdown()
            self.app.aboutToQuit.disconnect(owner.shutdown)
            self.app.processEvents()

    def exercise_companion(self, owner, clock, path):
        self.assertTrue(owner.pet.badge.text().endswith("50:00"))
        self.assertTrue(owner.pet.badge.toolTip().startswith("Ready · 50:00\n"))
        self.assertEqual(owner.timer.rest, 10)
        self.assertTrue(owner.walking)
        start = owner.pet.pos()
        QTest.qWait(180)
        self.assertNotEqual(owner.pet.pos(), start)

        context = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, QPoint(70, 80), owner.pet.pos() + QPoint(70, 80))
        self.app.sendEvent(owner.pet, context)
        self.assertTrue(owner.pet.menu.isVisible())
        owner.pet.menu.hide()
        owner.actions["options"].trigger()
        self.app.processEvents()
        self.assertTrue(owner.options.isVisible())
        self.assertEqual(owner.store.status(), QSettings.Status.NoError)
        self.save_render(owner.options, "options-en")
        owner.language_actions["ko"].trigger()
        self.app.processEvents()
        self.assertEqual(owner.options.windowTitle(), "Pawzura Pomodoro · 옵션")
        self.assertEqual(owner.language_menus[0].title(), "언어")
        self.save_render(owner.options, "options-ko")
        owner.options.language.setCurrentIndex(0)
        owner.options.language.activated.emit(0)
        self.assertTrue(owner.language_actions["en"].isChecked())
        owner.language_actions["ko"].trigger()
        owner.options.fields["work_minutes"].buddy().setValue(1)
        owner.options.fields["rest_minutes"].buddy().setValue(2)
        owner.options.close()

        owner.pet.badge.click()
        self.assertEqual(owner.timer.phase, "work")
        self.check_cues(owner, "work", 1000)
        self.assertIn("작업 시작", owner.cues.message)
        owner.cues.animation.setCurrentTime(500)
        self.check_pixels(owner, 0)
        self.save_render(next(iter(owner.cues.windows.values())), "cue-work-ko")
        owner.language_actions["en"].trigger()
        self.save_render(next(iter(owner.cues.windows.values())), "cue-work-en")
        owner.language_actions["ko"].trigger()
        self.assertIn(owner.actions["effects"], owner.tray_menu.actions())
        self.assertIn(owner.actions["effects"], owner.pet.menu.actions())
        owner.actions["effects"].trigger()
        self.assertFalse(owner.options.effects.isChecked())
        self.assertTrue(all(not widget.isVisible() for widget in owner.cues.windows.values()))
        self.assertEqual(owner.timer.phase, "work")
        owner.options.effects.click()
        self.assertTrue(owner.actions["effects"].isChecked())
        self.assertIsNone(owner.cues.phase)

        clock.now = 60
        owner.tick()
        self.check_cues(owner, "break", 3000)
        self.assertIn("2분", owner.cues.message)
        owner.cues.animation.setCurrentTime(1500)
        self.check_pixels(owner, 95)
        self.save_render(owner.pet, "companion-break-ko")
        self.save_render(next(iter(owner.cues.windows.values())), "cue-break-ko")
        owner.language_actions["en"].trigger()
        self.assertEqual(owner.cues.message, "Take a break · 2 min")
        self.save_render(next(iter(owner.cues.windows.values())), "cue-break-en")
        owner.cues.animation.setCurrentTime(3000)
        self.assertIsNone(owner.cues.phase)
        self.assertTrue(all(not widget.isVisible() for widget in owner.cues.windows.values()))
        clock.now = 180
        owner.tick()
        self.assertTrue(owner.pet.badge.text().endswith("01:00"))
        self.assertTrue(owner.pet.badge.toolTip().startswith("Start · 01:00\n"))
        self.assertEqual(owner.cues.phase, "waiting")
        self.assertIsNone(owner.timer.deadline)
        owner.actions["effects"].trigger()
        owner.pet.badge.click()
        self.assertEqual(owner.timer.phase, "work")
        self.assertIsNone(owner.cues.phase)

        self.drag_pet(owner)
        self.assertFalse(owner.walking)
        self.assertFalse(owner.actions["walking"].isChecked())
        self.assertTrue(owner.pet.pinned)
        owner.language_actions["ko"].trigger()
        self.assertEqual(owner.store.status(), QSettings.Status.NoError)
        self.assertIn("language=ko", path.read_text(encoding="utf-8"))
        saved = QSettings(str(path), QSettings.Format.IniFormat)
        self.assertEqual(saved.value("language"), "ko")
        self.assertEqual(saved.value("work", type=int), 1)
        self.assertEqual(saved.value("rest", type=int), 2)
        self.assertFalse(saved.value("effects", type=bool))
        self.assertFalse(saved.value("walking", type=bool))
        self.assertEqual(saved.value("position"), owner.pet.pos())
        owner.actions["walking"].trigger()
        self.assertTrue(owner.walking)
        self.assertFalse(owner.pet.pinned)
        self.save_render(owner.pet, "companion-ko")
        folder = os.environ.get("POMODORO_TEST_RENDERS")
        if folder:
            self.assertTrue(owner.tray.icon().pixmap(32, 32).save(str(Path(folder) / "tray.png")))

    def drag_pet(self, owner):
        left = Qt.MouseButton.LeftButton
        none = Qt.MouseButton.NoButton
        local = QPointF(72, 88)
        position = QPointF(owner.pet.pos()) + local
        current_screen = owner.pet.windowHandle().screen()
        other_screen = min(
            (screen for screen in self.app.screens() if screen != current_screen),
            key=lambda screen: screen.geometry().x(),
            default=None,
        )
        target = QPointF(other_screen.availableGeometry().center()) if other_screen else position + QPointF(-40, -65)
        for kind, button, held, global_pos in (
            (QEvent.Type.MouseButtonPress, left, left, position),
            (QEvent.Type.MouseMove, none, left, target),
            (QEvent.Type.MouseButtonRelease, left, none, target),
        ):
            event = QMouseEvent(kind, local, global_pos, button, held, Qt.KeyboardModifier.NoModifier)
            self.app.sendEvent(owner.pet, event)
        self.assertEqual(owner.pet.pos(), (target - local).toPoint())
        self.assertEqual(owner.pet.windowHandle().screen(), other_screen or current_screen)

    def check_cues(self, owner, phase, duration):
        self.app.processEvents()
        self.assertEqual(owner.cues.phase, phase)
        self.assertEqual(owner.cues.animation.duration(), duration)
        screens = self.app.screens()
        self.assertGreater(len(screens), 0)
        self.assertEqual(set(owner.cues.windows), set(screens))
        for screen, widget in owner.cues.windows.items():
            self.assertEqual(widget.geometry(), screen.geometry())
            self.assertTrue(widget.isVisible())
            self.assertTrue(widget.windowFlags() & Qt.WindowType.WindowTransparentForInput)
            self.assertTrue(widget.windowFlags() & Qt.WindowType.WindowDoesNotAcceptFocus)
            if sys.platform == "win32" and self.app.platformName() == "windows":
                extended_style = ctypes.windll.user32.GetWindowLongPtrW
                extended_style.argtypes = (ctypes.c_void_p, ctypes.c_int)
                extended_style.restype = ctypes.c_ssize_t
                style = extended_style(int(widget.winId()), -20)
                self.assertEqual(style & 0x08080020, 0x08080020)

    def check_pixels(self, owner, background_alpha):
        for widget in owner.cues.windows.values():
            image = widget.grab().toImage()
            self.assertEqual(image.pixelColor(image.width() // 4, image.height() // 4).alpha(), background_alpha)

    def save_render(self, widget, name):
        folder = os.environ.get("POMODORO_TEST_RENDERS")
        if folder:
            self.assertTrue(widget.grab().save(str(Path(folder) / f"{name}.png")))
