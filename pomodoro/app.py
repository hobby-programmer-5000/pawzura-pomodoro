from pathlib import Path
import sys

from PySide6.QtCore import QLockFile, QPoint, QSettings, QTimer, Qt
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMenu, QMessageBox, QSystemTrayIcon,
)

from .effects import EVENTS, Effect, ScreenCues
from .options import Options
from .surfaces import TimerPet, draw_tomato
from .text import TEXT
from .timer import MAX_MINUTES, PomodoroTimer


TITLE = "Pawzura Pomodoro"


class Companion:
    def __init__(self, app, store, clock=None, show_tray=True):
        self.app = app
        self.store = store
        self.language = self.read_language(store)
        self.effects = store.value("effects", True, type=bool)
        self.cue_settings = {event: Effect.load(store, event) for event in EVENTS}
        try:
            snooze = int(store.value("snooze_minutes", 2))
        except (TypeError, ValueError, OverflowError):
            snooze = 2
        self.snooze_minutes = snooze if 1 <= snooze <= 30 else 2
        self.remind_at = None
        self.walking = store.value("walking", True, type=bool)
        self.direction = "left" if store.value("direction") == "left" else "right"
        work = self.read_minutes("work", 50)
        rest = self.read_minutes("rest", 10)
        self.timer = PomodoroTimer(work, rest) if clock is None else PomodoroTimer(work, rest, clock)
        self.cues = ScreenCues(app)
        self.cues.action_requested.connect(self.cue_action)
        self.options = None
        self.pet = TimerPet(self.language, self.direction)
        position = store.value("position")
        if not self.walking:
            saved = {"x": position.x(), "y": position.y()} if isinstance(position, QPoint) else None
            self.pet.set_placement(True, saved)
        self.pet.settings_requested.connect(self.show_options)
        self.pet.placement_changed.connect(self.save_placement)
        self.pet.badge.clicked.connect(self.toggle)
        self.pet.menu = QMenu(self.pet)
        self.tray_menu = QMenu()
        menus = (self.pet.menu, self.tray_menu)
        self.actions = {}
        self.language_menus = []
        group = QActionGroup(self.pet)
        self.language_actions = {}
        for code, name in (("en", "English"), ("ko", "한국어")):
            action = QAction(name, group)
            action.setCheckable(True)
            action.triggered.connect(lambda _checked, language=code: self.set_language(language))
            self.language_actions[code] = action
        for key, callback in (
            ("options", self.show_options), ("toggle", self.toggle), ("reset", self.reset),
            ("effects", self.set_effects), ("effects_options", self.show_effect_options),
            ("dismiss", self.dismiss_effect), ("walking", self.set_walking), ("home", self.recover_pet),
            ("quit", app.quit),
        ):
            action = QAction(self.pet)
            action.setCheckable(key in ("effects", "walking"))
            action.triggered.connect(callback)
            self.actions[key] = action
            for menu in menus:
                if key in ("effects", "quit"):
                    menu.addSeparator()
                if key == "quit":
                    languages = menu.addMenu("")
                    for language_action in self.language_actions.values():
                        languages.addAction(language_action)
                    self.language_menus.append(languages)
                menu.addAction(action)

        self.tray = QSystemTrayIcon(self.make_icon(), app)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self.tray_activated)
        if show_tray:
            self.tray.show()
        self.last_display = None
        self.cues.changed.connect(self.refresh_effect_action)
        self.refresh()
        self.refresh_effect_action()
        self.pet.show()
        self.poll = QTimer(app)
        self.poll.timeout.connect(self.tick)
        self.poll.start(150)
        app.aboutToQuit.connect(self.shutdown)

    @staticmethod
    def read_language(store):
        return "ko" if store.value("language") == "ko" else "en"

    @property
    def text(self):
        return TEXT[self.language]

    def read_minutes(self, key, default):
        try:
            value = int(self.store.value(key, default))
        except (TypeError, ValueError, OverflowError):
            return default
        return value if 1 <= value <= MAX_MINUTES else default

    def save(self, **values):
        for key, value in values.items():
            self.store.setValue(key, value)
        self.store.sync()
        self.refresh()

    def make_icon(self):
        pixmap = QPixmap(128, 128)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.translate(-8, -19)
        draw_tomato(painter)
        painter.end()
        return QIcon(pixmap)

    def toggle_label(self):
        key = "start" if self.timer.ready_to_start else "resume" if self.timer.paused else "pause"
        return self.text[key]

    def countdown(self, compact=False):
        key = "paused" if self.timer.paused else self.timer.phase
        if compact and self.timer.phase == "waiting":
            key = "waiting_badge"
        minutes, seconds = divmod(self.timer.seconds, 60)
        return f"{self.text[key]} · {minutes:02d}:{seconds:02d}"

    def refresh(self):
        for key, action in self.actions.items():
            if key != "toggle":
                action.setText(self.text[key])
        self.actions["effects"].setChecked(self.effects)
        self.actions["walking"].setChecked(self.walking)
        self.language_actions[self.language].setChecked(True)
        for menu in self.language_menus:
            menu.setTitle(self.text["language"])
        self.pet.setToolTip(self.text["pet_hint"])
        if self.options:
            self.options.refresh()
        self.update_display()
        self.update_cue_text()

    def update_display(self):
        display = self.countdown(), self.toggle_label()
        if display == self.last_display:
            return
        self.last_display = display
        countdown, action = display
        self.actions["toggle"].setText(action)
        self.actions["reset"].setEnabled(self.timer.phase != "ready")
        self.pet.set_countdown(self.countdown(compact=True), action, self.timer.phase == "break")
        self.tray.setToolTip(f"{TITLE} · {countdown}")
        if self.options:
            self.options.update_timer(countdown, action)
        self.update_cue_text()

    def tick(self):
        self.handle_transition(self.timer.advance())
        if self.remind_at is not None and self.timer.clock() >= self.remind_at:
            self.remind_at = None
            if self.effects and self.timer.phase == "waiting":
                self.show_cue("waiting")

    def toggle(self):
        self.handle_transition(self.timer.toggle())

    def handle_transition(self, phase):
        if phase:
            self.remind_at = None
            self.cues.clear()
            if self.effects and phase in EVENTS:
                self.show_cue(phase)
        self.update_display()

    def cue_text(self, phase, preview=False):
        minutes = self.timer.work if phase == "waiting" else self.timer.minutes
        if preview:
            minutes = self.timer.rest if phase == "break" else self.timer.work
        message = self.text[f"{phase}_cue"].format(minutes=minutes)
        return f"{self.text['preview']} · {message}" if preview else message

    def cue_labels(self, preview=False):
        return {
            "start": self.text["start"],
            "snooze": self.text["snooze"].format(minutes=self.snooze_minutes),
            "dismiss": self.text["close_preview"] if preview else self.text["dismiss"],
            "off": self.text["effects_off"],
        }

    def cue_detail(self, phase, preview=False):
        if not preview:
            return self.countdown()
        minutes = self.timer.rest if phase == "break" else self.timer.work
        return f"{self.text[phase]} · {minutes:02d}:00"

    def show_cue(self, phase, preview=False):
        self.cues.show(
            phase, self.cue_settings[phase], self.cue_text(phase, preview), self.cue_detail(phase, preview),
            self.cue_labels(preview), self.pet.geometry().topLeft(), preview,
        )

    def update_cue_text(self):
        if self.cues.phase:
            self.cues.anchor = self.pet.geometry().topLeft()
            self.cues.set_text(
                self.cue_text(self.cues.phase, self.cues.preview),
                self.cue_detail(self.cues.phase, self.cues.preview), self.cue_labels(self.cues.preview),
            )

    def refresh_effect_action(self):
        self.actions["dismiss"].setEnabled(self.cues.phase is not None or self.remind_at is not None)

    def cue_action(self, action):
        if action == "off":
            self.set_effects(False)
        elif action == "start" and self.timer.phase == self.cues.phase == "waiting":
            self.toggle()
        elif action == "snooze" and self.timer.phase == self.cues.phase == "waiting":
            self.cues.clear()
            self.remind_at = self.timer.clock() + self.snooze_minutes * 60
            self.refresh_effect_action()
        elif action == "dismiss":
            self.dismiss_effect()

    def dismiss_effect(self):
        self.remind_at = None
        self.cues.clear()

    def preview_effect(self, event):
        self.show_cue(event, preview=True)

    def set_cue(self, event, style, retention, seconds, anywhere):
        self.cue_settings[event] = Effect(style, retention, seconds, anywhere)
        self.cue_settings[event].save(self.store, event)
        self.save()
        if self.cues.phase == event:
            self.show_cue(event, self.cues.preview)

    def set_snooze(self, minutes):
        self.snooze_minutes = minutes
        self.save(snooze_minutes=minutes)

    def reset(self):
        self.timer.reset()
        self.handle_transition("ready")

    def set_language(self, language):
        self.language = language
        self.save(language=language)

    def set_work(self, minutes):
        self.timer.work = minutes
        self.save(work=minutes)

    def set_rest(self, minutes):
        self.timer.rest = minutes
        self.save(rest=minutes)

    def set_effects(self, enabled):
        self.effects = enabled
        if not enabled:
            self.remind_at = None
            self.cues.clear()
        self.save(effects=enabled)
        if enabled and self.timer.phase == "waiting":
            self.show_cue("waiting")

    def set_direction(self, direction):
        self.direction = direction
        self.pet.set_walk_direction(direction)
        self.save(direction=direction)

    def set_walking(self, enabled):
        self.pet.set_placement(not enabled)
        self.walking = enabled
        if enabled:
            self.save(walking=True)
        else:
            self.save_placement(self.pet.resting_position())

    def save_placement(self, position):
        self.walking = False
        self.save(walking=False, position=QPoint(position["x"], position["y"]))

    def recover_pet(self):
        self.pet.reset_pointer()
        self.pet.home()
        if not self.walking:
            self.save_placement(self.pet.resting_position())

    def show_options(self):
        self.dismiss_effect()
        if self.options is None:
            self.options = Options(self)
        self.options.refresh()
        self.options.show()
        self.options.raise_()
        self.options.activateWindow()

    def show_effect_options(self):
        self.show_options()
        self.options.tabs.setCurrentIndex(1)

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_options()

    def shutdown(self):
        self.poll.stop()
        self.remind_at = None
        self.cues.dispose()
        self.tray.hide()
        self.pet.dispose()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(TITLE)
    app.setQuitOnLastWindowClosed(False)
    store = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Pawzura", "Pomodoro")
    store.setFallbacksEnabled(False)
    text = TEXT[Companion.read_language(store)]
    folder = Path(store.fileName()).parent
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError:
        QMessageBox.warning(None, TITLE, text["storage_error"])
        return 1
    lock = QLockFile(str(folder / "pomodoro.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        key = "already_open" if lock.error() == QLockFile.LockError.LockFailedError else "storage_error"
        QMessageBox.information(None, TITLE, text[key])
        return 1
    companion = Companion(app, store)
    app.setWindowIcon(companion.tray.icon())
    return app.exec()
