import os
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4

from PySide6.QtCore import QPoint, QSettings, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionButton

from pomodoro.app import Companion
from pomodoro.effects import DEFAULTS, EVENTS, STYLES, Effect


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


class EffectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.folder = Path(tempfile.gettempdir()) / f"pomodoro-effects-{uuid4().hex}"
        self.folder.mkdir()
        self.path = self.folder / "settings.ini"
        self.store = QSettings(str(self.path), QSettings.Format.IniFormat)
        self.clock = Clock()
        self.owner = Companion(self.app, self.store, self.clock, show_tray=False)

    def tearDown(self):
        if self.owner.options:
            self.owner.options.close()
        self.owner.shutdown()
        self.app.aboutToQuit.disconnect(self.owner.shutdown)
        self.app.processEvents()
        self.path.unlink(missing_ok=True)
        self.folder.rmdir()

    def finish_break(self):
        self.owner.set_work(1)
        self.owner.set_rest(1)
        self.owner.toggle()
        self.clock.now = 60
        self.owner.tick()
        self.clock.now = 120
        self.owner.tick()
        self.assertEqual(self.owner.timer.phase, "waiting")

    def first_window(self):
        return next(iter(self.owner.cues.windows.values()))

    def test_first_waiting_buttons_fit_after_timed_preview(self):
        owner = self.owner
        owner.set_language("ko")
        owner.set_cue("work", "edge", "timed", 1, True)
        owner.set_cue("waiting", "edge", "click", 2, True)
        owner.set_effects(False)
        self.finish_break()
        owner.preview_effect("work")
        owner.cues.animation.setCurrentTime(1000)
        self.app.processEvents()
        owner.set_effects(True)
        owner.cues.animation.setCurrentTime(220)
        self.app.processEvents()
        for window in owner.cues.windows.values():
            for name, button in window.buttons.items():
                with self.subTest(button=name):
                    self.assertTrue(button.isVisible())
                    option = QStyleOptionButton()
                    option.initFrom(button)
                    option.rect = button.rect()
                    contents = button.style().subElementRect(
                        QStyle.SubElement.SE_PushButtonContents, option, button,
                    )
                    self.assertGreaterEqual(contents.height(), button.fontMetrics().height())
                    self.assertGreaterEqual(button.height(), button.sizeHint().height())

    def test_waiting_needs_confirmation_and_rejects_old_callbacks(self):
        self.finish_break()
        cues = self.owner.cues
        window = self.first_window()
        old_token = cues.generation
        old_start = window.callbacks["start"]
        self.assertFalse(window.windowFlags() & Qt.WindowType.WindowTransparentForInput)
        cues.animation.setCurrentTime(220)
        self.clock.now = 2000
        self.owner.tick()
        self.assertEqual(cues.phase, "waiting")
        self.assertIsNone(self.owner.timer.deadline)
        self.assertEqual(self.owner.timer.seconds, 60)
        self.assertLessEqual(self.owner.pet.badge.width(), self.owner.pet.width())
        self.owner.set_language("ko")
        self.assertLessEqual(self.owner.pet.badge.width(), self.owner.pet.width())
        window.buttons["start"].click()
        self.assertEqual(self.owner.timer.phase, "work")
        self.assertEqual(self.owner.timer.seconds, 60)
        old_start()
        cues.request_action(old_token, "off")
        self.assertFalse(self.owner.timer.paused)
        self.assertTrue(self.owner.effects)
        self.owner.reset()
        old_start()
        self.assertEqual(self.owner.timer.phase, "ready")
        self.assertIsNone(self.owner.timer.deadline)

    def test_snooze_off_and_reset_cancel_pending_alerts(self):
        self.finish_break()
        self.first_window().buttons["snooze"].click()
        self.assertIsNone(self.owner.cues.phase)
        self.assertEqual(self.owner.remind_at, 240)
        self.clock.now = 239
        self.owner.tick()
        self.assertIsNone(self.owner.cues.phase)
        self.clock.now = 240
        self.owner.tick()
        self.assertEqual(self.owner.cues.phase, "waiting")
        self.first_window().buttons["snooze"].click()
        self.owner.set_effects(False)
        self.clock.now = 500
        self.owner.tick()
        self.assertIsNone(self.owner.remind_at)
        self.assertIsNone(self.owner.cues.phase)
        self.owner.set_effects(True)
        self.first_window().buttons["snooze"].click()
        self.owner.reset()
        self.clock.now = 1000
        self.owner.tick()
        self.assertIsNone(self.owner.remind_at)
        self.assertIsNone(self.owner.cues.phase)
        self.assertEqual(self.owner.timer.phase, "ready")

    def test_all_styles_preview_without_starting_timer(self):
        for language in ("en", "ko"):
            self.owner.set_language(language)
            for style in STYLES:
                with self.subTest(language=language, style=style):
                    self.owner.set_cue("waiting", style, "click", 3, False)
                    self.owner.preview_effect("waiting")
                    cues = self.owner.cues
                    cues.animation.setCurrentTime(220)
                    self.app.processEvents()
                    self.assertEqual(set(cues.windows), set(self.app.screens()))
                    for screen, window in cues.windows.items():
                        self.assertEqual(window.geometry(), screen.geometry())
                        self.assertTrue(window.isVisible())
                        self.assertFalse(window.buttons["start"].isVisible())
                        self.assertTrue(window.rect().contains(window.panel.geometry()))
                    folder = os.environ.get("POMODORO_TEST_RENDERS")
                    if folder:
                        self.assertTrue(self.first_window().grab().save(str(Path(folder) / f"{style}-{language}.png")))
                    cues.request_action(cues.generation, "start")
                    self.assertIsNone(cues.phase)
                    self.assertEqual(self.owner.timer.phase, "ready")
                    self.assertIsNone(self.owner.timer.deadline)

    def test_timed_interval_and_anywhere_dismissal(self):
        owner = self.owner
        owner.set_cue("work", "edge", "interval", 1, False)
        owner.toggle()
        owner.cues.animation.setCurrentTime(220)
        self.assertEqual(owner.cues.phase, "work")
        owner.toggle()
        self.assertTrue(owner.timer.paused)
        self.assertEqual(owner.cues.phase, "work")
        self.assertIn("Paused", self.first_window().detail.text())
        owner.toggle()
        owner.dismiss_effect()
        self.assertFalse(owner.timer.paused)
        self.finish_current_work_and_break()
        owner.set_cue("waiting", "cover", "click", 3, True)
        window = self.first_window()
        QTest.mousePress(window, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
        owner.show_cue("waiting")
        QTest.mouseRelease(window, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
        self.assertEqual(owner.cues.phase, "waiting")
        QTest.mouseClick(window, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
        self.assertIsNone(owner.cues.phase)
        self.assertEqual(owner.timer.phase, "waiting")
        for style in STYLES:
            owner.set_cue("work", style, "timed", 2, False)
            owner.preview_effect("work")
            self.assertEqual(owner.cues.animation.duration(), 2000)
            self.assertEqual(
                bool(self.first_window().windowFlags() & Qt.WindowType.WindowTransparentForInput),
                style != "cover",
            )
            owner.cues.animation.setCurrentTime(2000)
            self.assertIsNone(owner.cues.phase)

    def finish_current_work_and_break(self):
        self.clock.now = self.owner.timer.deadline
        self.owner.tick()
        self.clock.now = self.owner.timer.deadline
        self.owner.tick()
        self.assertEqual(self.owner.timer.phase, "waiting")

    def test_options_persist_per_event_and_invalid_settings_fall_back(self):
        owner = self.owner
        owner.actions["effects_options"].trigger()
        ui = owner.options.effect_options
        self.assertEqual(owner.options.tabs.currentIndex(), 1)
        self.assertEqual(ui.event.currentData(), "waiting")
        index = ui.style.findData("cover")
        ui.style.setCurrentIndex(index)
        ui.style.activated.emit(index)
        self.assertEqual(owner.cue_settings["waiting"].style, "cover")
        ui.anywhere.click()
        ui.snooze.setValue(5)
        for event in EVENTS:
            if event != "waiting":
                owner.set_cue(event, "banner", "interval", 9, False)
        disk = QSettings(str(self.path), QSettings.Format.IniFormat)
        self.assertEqual(disk.status(), QSettings.Status.NoError)
        for event in EVENTS:
            self.assertEqual(Effect.load(disk, event), owner.cue_settings[event])
        self.assertEqual(disk.value("snooze_minutes", type=int), 5)
        disk.setValue("cues/waiting/style", "bad")
        disk.setValue("cues/waiting/retention", "interval")
        disk.setValue("cues/waiting/seconds", "bad")
        self.assertEqual(Effect.load(disk, "waiting"), Effect("dim", "click", 3, True))
        disk.remove("cues")
        for event in EVENTS:
            self.assertEqual(Effect.load(disk, event), DEFAULTS[event])
        for language in ("en", "ko"):
            owner.set_language(language)
            owner.options.refresh()
            self.app.processEvents()
            folder = os.environ.get("POMODORO_TEST_RENDERS")
            if folder:
                self.assertTrue(owner.options.grab().save(str(Path(folder) / f"effects-options-{language}.png")))
