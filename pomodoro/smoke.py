"""Exercise the real widgets using disposable settings; never load a user profile."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
from uuid import uuid4

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionButton

from . import __version__
from .app import Companion
from .effects import STYLES


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check(render_dir=None):
    app = QApplication.instance() or QApplication([sys.argv[0]])
    app.setQuitOnLastWindowClosed(False)
    folder = Path(tempfile.gettempdir()) / f"pomodoro-smoke-{uuid4().hex}"
    folder.mkdir()
    owner = None
    now = [0.0]
    report = {"version": __version__, "frozen": bool(getattr(sys, "frozen", False)),
              "clock": "synthetic", "settings": "disposable INI", "checks": []}
    try:
        store = QSettings(str(folder / "settings.ini"), QSettings.Format.IniFormat)
        store.setFallbacksEnabled(False)
        owner = Companion(app, store, lambda: now[0], show_tray=False)
        require((owner.language, owner.timer.work, owner.timer.rest) == ("en", 50, 10), "Fresh defaults")
        require(owner.walking and owner.effects and owner.timer.phase == "ready", "Fresh controls")
        require(owner.cue_settings["waiting"].style == "dim", "Default waiting cue")
        require(bool(app.screens()), "No Qt screens")
        report["checks"].append("clean defaults: English, 50/10, walking/effects on, ready")
        for language in ("en", "ko"):
            now[0] = 0.0
            owner.reset()
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
            now[0] = 120
            owner.tick()
            require(owner.timer.phase == "waiting" and owner.timer.deadline is None, "Explicit restart")
            owner.set_cue("work", "edge", "timed", 1, True)
            owner.set_cue("waiting", "edge", "click", 2, True)
            owner.set_effects(False)
            owner.preview_effect("work")
            owner.cues.animation.setCurrentTime(1000)
            app.processEvents()
            owner.set_effects(True)
            owner.cues.animation.setCurrentTime(220)
            app.processEvents()
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
                app.processEvents()
                for screen, window in owner.cues.windows.items():
                    require(window.geometry() == screen.geometry(), "Screen geometry")
                    require(window.buttons["dismiss"].isVisible() and not window.buttons["start"].isVisible(), "Safe preview")
                require(owner.timer.phase == "waiting", "Preview does not start work")
            owner.dismiss_effect()
            owner.show_cue("waiting")
            old_start = next(iter(owner.cues.windows.values())).callbacks["start"]
            next(iter(owner.cues.windows.values())).buttons["start"].click()
            require(owner.timer.phase == "work" and owner.timer.seconds == 60, "Confirm work")
            owner.reset()
            old_start()
            require(owner.timer.phase == "ready", "Stale action rejected")
            owner.show_options()
            app.processEvents()
            require(owner.options.isVisible(), "Options visible")
            owner.options.close()
            report["checks"].append(f"{language}: cycle, pause/resume, five previews, all-screen button layout, confirm, cancellation, options")
        disk = QSettings(str(folder / "settings.ini"), QSettings.Format.IniFormat)
        require(disk.value("language") == "ko" and disk.value("work", type=int) == 1, "Persistence")
        require(disk.status() == QSettings.Status.NoError, "Settings status")
        report.update(status="PASS", screens=len(app.screens()))
        return report
    finally:
        if owner:
            if owner.options:
                owner.options.close()
            owner.shutdown()
            app.aboutToQuit.disconnect(owner.shutdown)
            app.processEvents()
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
