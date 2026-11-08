from pathlib import Path
import shutil
import tempfile
import unittest
from uuid import uuid4

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from pomodoro.app import Companion
from pomodoro.settings import create_settings


class SettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.folder = Path(tempfile.gettempdir()) / f"pomodoro-profile-{uuid4().hex}"
        self.folder.mkdir()
        probe = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope,
                          "PawzuraPomodoro", "Desktop")
        self.previous_root = Path(probe.fileName()).parent.parent
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(self.folder))
        self.owners = []

    def tearDown(self):
        for owner in self.owners:
            if owner.options:
                owner.options.close()
            owner.shutdown()
            self.app.aboutToQuit.disconnect(owner.shutdown)
        self.app.processEvents()
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(self.previous_root))
        self.assertEqual(self.folder.resolve().parent, Path(tempfile.gettempdir()).resolve())
        shutil.rmtree(self.folder)

    def owner(self, store):
        owner = Companion(self.app, store, show_tray=False)
        self.owners.append(owner)
        return owner

    def test_legacy_and_development_values_do_not_pollute_desktop_defaults(self):
        old = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Pawzura", "Pomodoro")
        old.setValue("work", 1)
        old.setValue("rest", 10)
        old.sync()
        old_bytes = Path(old.fileName()).read_bytes()
        dev = create_settings(frozen=False)
        dev.setValue("work", 1)
        dev.setValue("rest", 2)
        dev.sync()
        desktop = create_settings(frozen=True)
        self.assertNotEqual(desktop.fileName(), dev.fileName())
        self.assertNotEqual(desktop.fileName(), old.fileName())
        self.assertTrue(Path(desktop.fileName()).resolve().is_relative_to(self.folder.resolve()))
        owner = self.owner(desktop)
        self.assertEqual((owner.timer.work, owner.timer.rest, owner.timer.seconds), (50, 10, 3000))
        self.assertIsNone(owner.startup)
        self.assertEqual(Path(old.fileName()).read_bytes(), old_bytes)

    def test_desktop_preferences_survive_reopening_and_explicit_profile_is_honored(self):
        owner = self.owner(create_settings(frozen=True))
        owner.set_work(23)
        owner.set_rest(7)
        again = self.owner(create_settings(frozen=True))
        self.assertEqual((again.timer.work, again.timer.rest), (23, 7))
        path = self.folder / "custom.ini"
        explicit = create_settings(path, frozen=True)
        explicit.setValue("work", 1)
        explicit.sync()
        custom = self.owner(create_settings(path, frozen=True))
        self.assertEqual((custom.timer.work, custom.timer.rest), (1, 10))

    def test_restore_durations_updates_options_and_next_interval_without_interrupting(self):
        owner = self.owner(create_settings(frozen=True))
        owner.set_work(1)
        owner.set_rest(2)
        owner.toggle()
        deadline = owner.timer.deadline
        owner.show_options()
        owner.options.restore_durations.click()
        self.assertEqual((owner.timer.work, owner.timer.rest), (50, 10))
        self.assertEqual((owner.timer.phase, owner.timer.deadline), ("work", deadline))
        self.assertEqual(owner.options.durations["work_minutes"].value(), 50)
        self.assertEqual(owner.options.durations["rest_minutes"].value(), 10)
        owner.reset()
        self.assertEqual(owner.timer.seconds, 3000)
