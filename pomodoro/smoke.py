"""Exercise the real widgets using disposable settings; never load a user profile."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
from uuid import uuid4

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionButton

from . import __version__
from .app import Companion
from .effects import STYLES
from .settings import create_settings
from .startup import Startup


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check(render_dir=None):
    app = QApplication.instance() or QApplication([sys.argv[0]])
    app.setQuitOnLastWindowClosed(False)
    folder = Path(tempfile.gettempdir()) / f"pomodoro-smoke-{uuid4().hex}"
    folder.mkdir()
    owner = None
    probe = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "PawzuraPomodoro", "Desktop")
    previous_root = Path(probe.fileName()).parent.parent
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(folder / "profiles"))
    now, pose_now = [0.0], [0.0]
    report = {"version": __version__, "frozen": bool(getattr(sys, "frozen", False)),
              "clock": "synthetic", "settings": "disposable INI", "checks": []}
    try:
        legacy = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Pawzura", "Pomodoro")
        legacy.setValue("work", 1)
        legacy.sync()
        legacy_bytes = Path(legacy.fileName()).read_bytes()
        development = create_settings(frozen=False)
        development.setValue("work", 1)
        development.sync()
        store = create_settings() if getattr(sys, "frozen", False) else create_settings(frozen=True)
        require(store.fileName() not in (legacy.fileName(), development.fileName()), "Profile separation")
        class MemoryRunKey:
            value = None

            def read(self):
                return self.value

            def write(self, command):
                self.value = command

            def delete(self):
                self.value = None

        startup = Startup(sys.executable, MemoryRunKey())
        owner = Companion(app, store, lambda: now[0], show_tray=False, startup=startup, pose_clock=lambda: pose_now[0])
        owner.pet.timer.stop()

        def pose_step(delta, expected, language, name):
            pose_now[0] += delta
            owner.pet.tick()
            require(owner.pet.posture.state == expected, f"{language}: {name} posture")
            app.processEvents()
            if render_dir:
                require(owner.pet.grab().save(str(render_dir / f"pet-{language}-{name}.png")), "Pet render")
        # This diagnostic drives widget actions directly, not OS pointer input.
        # Let real desktop clicks pass through its temporary test surfaces.
        owner.pet.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        owner.pet.show()

        def settle():
            for window in owner.cues.windows.values():
                if window.isVisible():
                    window.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
                    window.show()
            app.processEvents()
        require((owner.language, owner.timer.work, owner.timer.rest) == ("en", 50, 10), "Fresh defaults")
        require(owner.walking and owner.effects and owner.timer.phase == "ready", "Fresh controls")
        require(owner.cue_settings["waiting"].style == "dim", "Default waiting cue")
        require(bool(app.screens()), "No Qt screens")
        report["checks"].append("clean defaults: English, 50/10, walking/effects on, ready")
        report["checks"].append("legacy/development 1-minute settings do not affect the desktop profile")
        report["production_defaults"] = [owner.timer.work, owner.timer.rest]
        for language in ("en", "ko"):
            now[0] = 0.0
            owner.reset()
            pose_now[0] += 1
            owner.pet.tick()
            owner.set_language(language)
            owner.set_work(1)
            owner.set_rest(1)
            owner.toggle()
            require(owner.timer.phase == "work" and owner.timer.seconds == 60, "Start work")
            owner.toggle()
            require(owner.timer.paused, "Pause")
            owner.toggle()
            require(not owner.timer.paused, "Resume")
            now[0] = 60
            owner.tick()
            require(owner.timer.phase == "break", "Work to break")
            anchor = owner.pet.pos()
            pose_step(.3, "sitting_down", language, "sitting")
            require(owner.pet.pos() == anchor, "Sit anchored")
            pose_step(.4, "seated", language, "sleeping")
            require(owner.pet.resting and owner.pet.pos() == anchor, "Sleeping anchored")
            now[0] = 120
            owner.tick()
            require(owner.timer.phase == "waiting" and owner.timer.deadline is None, "Explicit restart")
            pose_step(1, "seated", language, "waiting")
            require(not owner.pet.resting and owner.pet.pos() == anchor, "Waiting seated with normal expression")
            owner.set_cue("work", "edge", "timed", 1, True)
            owner.set_cue("waiting", "edge", "click", 2, True)
            owner.set_effects(False)
            owner.preview_effect("work")
            owner.cues.animation.setCurrentTime(1000)
            settle()
            owner.set_effects(True)
            owner.cues.animation.setCurrentTime(220)
            settle()
            require(set(owner.cues.windows) == set(app.screens()), "All screens")
            for index, window in enumerate(owner.cues.windows.values()):
                require(window.isVisible(), "Waiting window visible")
                for button in window.buttons.values():
                    option = QStyleOptionButton()
                    option.initFrom(button)
                    option.rect = button.rect()
                    contents = button.style().subElementRect(QStyle.SubElement.SE_PushButtonContents, option, button)
                    require(button.isVisible() and contents.height() >= button.fontMetrics().height(), "Button text fits")
                    require(button.height() >= button.sizeHint().height(), "Button height fits")
                if render_dir:
                    require(window.panel.grab().save(str(render_dir / f"waiting-{language}-{index}.png")), "Panel render")
            for style in STYLES:
                owner.set_cue("waiting", style, "click", 2, True)
                owner.preview_effect("waiting")
                owner.cues.animation.setCurrentTime(220)
                settle()
                for screen, window in owner.cues.windows.items():
                    require(window.geometry() == screen.geometry(), "Screen geometry")
                    require(window.buttons["dismiss"].isVisible() and not window.buttons["start"].isVisible(),
                            f"Safe preview {language}/{style}: phase={owner.cues.phase}, preview={owner.cues.preview}, "
                            f"dismiss={window.buttons['dismiss'].isVisible()}, start={window.buttons['start'].isVisible()}")
                require(owner.timer.phase == "waiting", "Preview does not start work")
            owner.dismiss_effect()
            owner.show_cue("waiting")
            old_start = next(iter(owner.cues.windows.values())).callbacks["start"]
            next(iter(owner.cues.windows.values())).buttons["start"].click()
            require(owner.timer.phase == "work" and owner.timer.seconds == 60, "Confirm work")
            pose_step(.3, "standing_up", language, "rising")
            require(owner.pet.pos() == anchor, "Stand before travel")
            pose_step(.5, "standing", language, "standing")
            owner.reset()
            old_start()
            require(owner.timer.phase == "ready", "Stale action rejected")
            owner.show_options()
            owner.options.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
            owner.options.show()
            settle()
            require(owner.options.isVisible(), "Options visible")
            require(not owner.options.startup.isChecked(), "Startup defaults off")
            owner.options.startup.click()
            require(owner.options.startup.isChecked() and startup.enabled(), "Startup opt in (memory backend)")
            require(str(Path(sys.executable).resolve()) in startup.command, "External startup target")
            if getattr(sys, "frozen", False):
                require(not startup.executable.is_relative_to(Path(sys._MEIPASS).resolve()), "Startup must not target temporary/internal files")
            owner.options.startup.click()
            require(not startup.enabled(), "Startup opt out")
            owner.options.restore_durations.click()
            require((owner.timer.work, owner.timer.rest) == (50, 10), "Restore 50/10")
            if render_dir:
                require(owner.options.grab().save(str(render_dir / f"options-{language}.png")), "Options render")
            owner.options.licenses_button.click()
            if owner.options.licenses_dialog:
                owner.options.licenses_dialog.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
                owner.options.licenses_dialog.show()
            app.processEvents()
            require(owner.options.licenses_dialog and owner.options.licenses_dialog.isVisible(), "License notices available")
            owner.options.licenses_dialog.close()
            owner.set_work(1)
            owner.set_rest(1)
            owner.options.close()
            report["checks"].append(f"{language}: cycle, pause/resume, anchored sit/sleep/wait/rise, five previews, all-screen button layout, confirm, cancellation, options")
        disk = create_settings(frozen=True)
        require(disk.value("language") == "ko" and disk.value("work", type=int) == 1, "Persistence")
        require(disk.status() == QSettings.Status.NoError, "Settings status")
        require(Path(legacy.fileName()).read_bytes() == legacy_bytes, "Legacy profile preserved")
        require(not startup.enabled(), "Diagnostic leaves startup off")
        report["checks"].append("startup uses memory registry only; 50/10 restore and embedded license dialog")
        report.update(status="PASS", screens=len(app.screens()))
        return report
    finally:
        if owner:
            if owner.options:
                owner.options.close()
            owner.shutdown()
            app.aboutToQuit.disconnect(owner.shutdown)
            app.processEvents()
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(previous_root))
        # Only our UUID-named temporary directory is removed.
        require(folder.resolve().parent == Path(tempfile.gettempdir()).resolve(), "Temporary path containment")
        shutil.rmtree(folder)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-check", action="store_true", required=True)
    parser.add_argument("--smoke-output", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args(argv)
    if args.render_dir:
        args.render_dir.mkdir(parents=True, exist_ok=True)
    try:
        report = check(args.render_dir)
    except Exception:
        report = {"status": "FAIL", "version": __version__, "error": traceback.format_exc()}
    args.smoke_output.parent.mkdir(parents=True, exist_ok=True)
    args.smoke_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1
