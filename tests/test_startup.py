from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from pomodoro.app import Companion
from pomodoro.startup import Startup, command_args


class MemoryRunKey:
    def __init__(self):
        self.value = None
        self.fail = False

    def read(self):
        return self.value

    def write(self, command):
        if self.fail:
            raise PermissionError("Synthetic access denial")
        self.value = command

    def delete(self):
        self.value = None


class StartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.folder = Path(tempfile.gettempdir()) / f"pomodoro-startup-{uuid4().hex}"
        self.folder.mkdir()
        self.exe = self.folder / "PawzuraPomodoro 한글 demo.exe"
        self.exe.touch()
        self.registry = MemoryRunKey()
        self.startup = Startup(self.exe, self.registry)

    def tearDown(self):
        self.assertEqual(self.folder.resolve().parent, Path(tempfile.gettempdir()).resolve())
        shutil.rmtree(self.folder)

    def test_default_off_quotes_executable_and_removes_only_owned_entry(self):
        self.assertFalse(self.startup.enabled())
        self.assertIsNone(self.registry.value)
        self.startup.set_enabled(True)
        self.assertEqual(command_args(self.registry.value), [str(self.exe.resolve()), "--startup"])
        self.assertTrue(Startup(self.exe, self.registry).enabled())
        self.startup.set_enabled(False)
        self.assertIsNone(self.registry.value)
        self.registry.value = '"other-tool.exe" --launch'
        for enabled in (True, False):
            with self.assertRaises(ValueError):
                self.startup.set_enabled(enabled)
            self.assertEqual(self.registry.value, '"other-tool.exe" --launch')

    def test_missing_exe_or_write_failure_keeps_startup_off(self):
        self.registry.fail = True
        with self.assertRaises(PermissionError):
            self.startup.set_enabled(True)
        self.assertFalse(self.startup.enabled())
        self.exe.unlink()
        with self.assertRaises(ValueError):
            self.startup.set_enabled(True)
        self.assertIsNone(self.registry.value)

    def test_bilingual_checkbox_and_failed_write_restore_actual_state(self):
        store = QSettings(str(self.folder / "test.ini"), QSettings.Format.IniFormat)
        owner = Companion(self.app, store, show_tray=False, startup=self.startup)
        try:
            owner.show_options()
            for language in ("en", "ko"):
                owner.set_language(language)
                self.assertTrue(owner.options.startup.isEnabled())
                self.assertFalse(owner.options.startup.isChecked())
                owner.options.startup.click()
                self.assertTrue(owner.options.startup.isChecked())
                owner.options.startup.click()
                self.assertFalse(owner.options.startup.isChecked())
            self.registry.fail = True
            with patch("pomodoro.app.QMessageBox.warning") as warning:
                owner.options.startup.click()
                warning.assert_called_once()
                self.assertFalse(owner.options.startup.isChecked())
            self.assertIsNone(self.registry.value)
        finally:
            owner.options.close()
            owner.shutdown()
            self.app.aboutToQuit.disconnect(owner.shutdown)
            self.app.processEvents()
