from pathlib import Path
import tempfile
from time import monotonic
import unittest
from unittest.mock import patch

from PySide6.QtCore import QPoint, QPointF, QSettings
from PySide6.QtWidgets import QApplication

from pomodoro.app import Companion


class VisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="pomodoro-visibility-")
        self.store = QSettings(str(Path(self.folder.name) / "settings.ini"), QSettings.Format.IniFormat)
        self.now, self.pose = 0.0, 0.0
        self.owners = []
        self.owner = self.open()

    def open(self, show_tray=False):
        owner = Companion(self.app, self.store, lambda: self.now, show_tray=show_tray,
                          pose_clock=lambda: self.pose)
        self.owners.append(owner)
        return owner

    def tearDown(self):
        for owner in self.owners:
            if owner.options:
                owner.options.close()
            owner.shutdown()
            self.app.aboutToQuit.disconnect(owner.shutdown)
        self.app.processEvents()
        self.folder.cleanup()

    def test_menu_checkbox_and_localization_keep_controls_synchronized(self):
        owner = self.owner
        self.assertTrue(owner.pet_visible and owner.pet.isVisible())
        owner.show_options()
        for language in ("en", "ko"):
            owner.set_language(language)
            self.assertTrue(owner.options.pet_visible.isChecked())
            self.assertEqual(owner.actions["visibility"].text(), owner.text["hide_pet"])
            self.assertIn(owner.actions["visibility"], owner.tray_menu.actions())
            self.assertIn(owner.actions["visibility"], owner.pet.menu.actions())
            owner.actions["visibility"].trigger()
            self.assertFalse(owner.pet_visible or owner.pet.isVisible() or owner.pet.timer.isActive())
            self.assertTrue(owner.poll.isActive())
            self.assertFalse(owner.options.pet_visible.isChecked())
            self.assertEqual(owner.actions["visibility"].text(), owner.text["show_pet"])
            owner.options.pet_visible.click()
            self.assertTrue(owner.pet_visible and owner.pet.isVisible() and owner.pet.timer.isActive())

    def test_hidden_cycle_snooze_and_restore_keep_current_posture_and_timer(self):
        owner = self.owner
        owner.set_work(1)
        owner.set_rest(1)
        owner.set_cue("waiting", "edge", "click", 2, False)
        owner.set_pet_visible(False)
        owner.actions["toggle"].trigger()
        self.now = 60
        owner.tick()
        self.assertEqual((owner.timer.phase, owner.cues.phase), ("break", "break"))
        self.pose = 1
        self.now = 120
        owner.tick()
        self.assertEqual((owner.timer.phase, owner.cues.phase), ("waiting", "waiting"))
        owner.cue_action("snooze")
        reminder = owner.remind_at
        owner.set_pet_visible(True)
        self.assertEqual(owner.remind_at, reminder)
        self.assertEqual(owner.pet.posture.state, "seated")
        self.assertFalse(owner.pet.resting)
        owner.set_pet_visible(False)
        self.assertEqual(owner.remind_at, reminder)
        self.now = reminder
        owner.tick()
        self.assertEqual(owner.cues.phase, "waiting")
        self.assertFalse(owner.pet.isVisible() or owner.pet.timer.isActive())
        owner.cue_action("start")
        self.assertEqual(owner.timer.phase, "work")
        owner.set_pet_visible(True)
        self.assertEqual(owner.pet.posture.state, "standing_up")
        anchor = owner.pet.pos()
        owner.pet.last_tick = monotonic() - .05
        owner.pet.tick()
        self.assertEqual(owner.pet.pos(), anchor)
        self.assertTrue(owner.pet_visible)

    def test_hidden_persistence_preferences_recovery_and_no_catchup_jump(self):
        owner = self.owner
        owner.set_walking(False)
        position = self.store.value("position")
        self.assertIsInstance(position, QPoint)
        owner.pet.react("hop")
        owner.pet._press_global = QPointF(50, 50)
        owner.set_pet_visible(False)
        self.assertFalse(owner.pet.pointer_active)
        self.assertIsNone(owner.pet.reaction)
        for language in ("ko", "en"):
            owner.set_language(language)
            owner.set_character("classic")
            owner.set_effects(False)
            owner.reset()
            self.assertFalse(owner.pet.isVisible())
        again = self.open()
        self.assertFalse(again.pet_visible or again.pet.isVisible() or again.pet.timer.isActive())
        self.assertTrue(again.pet.pinned)
        self.assertFalse(again.walking)
        self.assertEqual(self.store.value("position"), position)
        again.pet.last_tick = monotonic() - 10000
        again.set_pet_visible(True)
        self.assertLess(monotonic() - again.pet.last_tick, 1)
        self.assertEqual(again.pet.pos(), position)
        self.assertEqual(self.store.value("position"), position)
        again.set_pet_visible(False)
        again.actions["home"].trigger()
        self.assertTrue(again.pet_visible and again.pet.isVisible() and again.pet.pinned)
        self.assertFalse(again.walking)
        # Restoring refits an obsolete position to current monitor work areas.
        again.set_pet_visible(False)
        again.pet.px, again.pet.py = -100000, -100000
        again.set_pet_visible(True)
        self.assertTrue(any(s.availableGeometry().contains(again.pet.geometry()) for s in self.app.screens()))

    def test_missing_tray_exposes_options_and_restores_when_closed_without_dismissing_cues(self):
        self.store.setValue("pet_visible", False)
        with patch("pomodoro.app.QSystemTrayIcon.isSystemTrayAvailable", return_value=False):
            owner = self.open(show_tray=True)
            self.assertTrue(owner.options.isVisible())
            self.assertFalse(owner.pet.isVisible())
            owner.show_cue("waiting")
            owner.set_pet_visible(False)
            self.assertEqual(owner.cues.phase, "waiting")
            owner.options.close()
            self.assertTrue(owner.pet_visible and owner.pet.isVisible())
            self.assertEqual(owner.cues.phase, "waiting")

    def test_compact_options_keep_visibility_and_bottom_controls_reachable(self):
        owner = self.owner
        owner.show_options()
        for language in ("en", "ko"):
            owner.set_language(language)
            owner.options.resize(600, 400)
            self.app.processEvents()
            scroll = owner.options.general_scroll
            scroll.ensureWidgetVisible(owner.options.pet_visible)
            self.app.processEvents()
            center = owner.options.pet_visible.mapTo(scroll.viewport(), owner.options.pet_visible.rect().center())
            self.assertTrue(scroll.viewport().rect().contains(center))
            self.assertTrue(owner.options.rect().contains(owner.options.close_button.geometry()))
            owner.options.pet_visible.click()
            self.assertFalse(owner.pet_visible)
            owner.options.pet_visible.click()
            self.assertTrue(owner.pet_visible)
            owner.options.tabs.setCurrentIndex(1)
            effect_scroll = owner.options.tabs.widget(1)
            effect_scroll.ensureWidgetVisible(owner.options.effect_options.preview)
            self.app.processEvents()
            preview = owner.options.effect_options.preview
            center = preview.mapTo(effect_scroll.viewport(), preview.rect().center())
            self.assertTrue(effect_scroll.viewport().rect().contains(center))
            owner.options.tabs.setCurrentIndex(0)


if __name__ == "__main__":
    unittest.main()
