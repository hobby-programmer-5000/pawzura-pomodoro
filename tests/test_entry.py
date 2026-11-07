"""Exercise the real entry point without reading the developer's settings."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from uuid import uuid4


@unittest.skipUnless(sys.platform == "win32", "Windows desktop entry point")
class EntryTests(unittest.TestCase):
    def test_explicit_profile_startup_and_restart_after_forced_stop(self):
        folder = Path(tempfile.gettempdir()) / f"pomodoro-entry-{uuid4().hex}"
        folder.mkdir()
        root = Path(__file__).resolve().parent.parent
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "windows"
        # Run the actual interpreter rather than Windows' venv redirector, so
        # Popen owns the Qt process handle and terminate/wait closes its lock.
        interpreter = Path(sys.base_prefix) / "python.exe"
        env["PYTHONPATH"] = os.pathsep.join(str(Path(p).resolve()) for p in sys.path if p)
        previous_pid = None
        try:
            for attempt in range(2):
                with self.subTest(attempt=attempt):
                    child = subprocess.Popen([str(interpreter), "-m", "pomodoro", "--settings-file", str(folder / "settings.ini")],
                                             cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try:
                        lock = folder / "pomodoro.lock"
                        matched = False
                        deadline = time.monotonic() + 12
                        while time.monotonic() < deadline and child.poll() is None:
                            try:
                                lock_pid = int(lock.read_text("utf-8").splitlines()[0])
                                matched = lock_pid == child.pid and lock_pid != previous_pid
                            except (OSError, IndexError, UnicodeError, ValueError):
                                matched = False
                            if matched:
                                break
                            time.sleep(.1)
                        self.assertTrue(matched, "The child must own the explicit profile's lock")
                        time.sleep(.8)
                        self.assertIsNone(child.poll(), "The normal event loop must remain running")
                        if attempt == 0:
                            duplicate = subprocess.run([str(interpreter), "-m", "pomodoro", "--settings-file",
                                                        str(folder / "settings.ini"), "--startup"],
                                                       cwd=root, env=env, stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE, timeout=10)
                            self.assertEqual(duplicate.returncode, 0, "A duplicate login start must exit quietly")
                            self.assertIsNone(child.poll())
                        previous_pid = lock_pid
                    finally:
                        if child.poll() is None:
                            child.terminate()
                        child.wait(timeout=15)
        finally:
            self.assertEqual(folder.resolve().parent, Path(tempfile.gettempdir()).resolve())
            shutil.rmtree(folder)
