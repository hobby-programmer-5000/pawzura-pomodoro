from dataclasses import dataclass

from PySide6.QtCore import QObject, QPoint, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .surfaces import draw_tomato


STYLES = ("edge", "bubble", "banner", "dim", "cover")
RETENTIONS = ("timed", "click", "interval")
EVENTS = ("work", "break", "waiting")


@dataclass(frozen=True)
class Effect:
    style: str
    retention: str
    seconds: int
    anywhere: bool = False

    @property
    def interactive(self):
        return self.retention != "timed" or self.style == "cover"

    @classmethod
    def load(cls, store, event):
        default = DEFAULTS[event]
        prefix = f"cues/{event}/"
        style = store.value(prefix + "style", default.style)
        retention = store.value(prefix + "retention", default.retention)
        try:
            seconds = int(store.value(prefix + "seconds", default.seconds))
        except (TypeError, ValueError, OverflowError):
            seconds = default.seconds
        return cls(
            style if style in STYLES else default.style,
            retention if retention in retention_choices(event) else default.retention,
            seconds if 1 <= seconds <= 60 else default.seconds,
            store.value(prefix + "anywhere", default.anywhere, type=bool),
        )

    def save(self, store, event):
        for name, value in vars(self).items():
            store.setValue(f"cues/{event}/{name}", value)


DEFAULTS = {
    "work": Effect("edge", "timed", 1),
    "break": Effect("dim", "timed", 3),
    "waiting": Effect("dim", "click", 3),
}


def retention_choices(event):
    return RETENTIONS[:2] if event == "waiting" else RETENTIONS


class TomatoStamp(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(76, 76)
        self.resting = False

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.scale(.6, .6)
        painter.translate(-8, -20)
        draw_tomato(painter, resting=self.resting)
        painter.end()


class ScreenCue(QWidget):
    command = Signal(int, str)

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle("Pawzura Pomodoro")
        self.phase = None
        self.strength = 0.0
        self.token = 0
        self.press_token = None
        self.effect = DEFAULTS["work"]
        self.preview = False
        self.panel = QWidget(self)
        self.panel.setObjectName("cuePanel")
        self.panel.setStyleSheet("""
            QWidget#cuePanel { background: #253248; border-radius: 16px; }
            QLabel { color: #f4f8ff; background: transparent; }
            QPushButton {
                background: #364760; color: #f4f8ff; border: 1px solid #8292a9;
                border-radius: 7px; padding: 8px 12px;
            }
            QPushButton:hover { background: #48617f; }
            QPushButton#start { background: #a8decd; color: #17392e; }
        """)
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(9)
        self.tomato = TomatoStamp(self.panel)
        layout.addWidget(self.tomato, alignment=Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel()
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title.font()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        layout.addWidget(self.title)
        self.detail = QLabel()
        self.detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.detail)
        grid = QGridLayout()
        layout.addLayout(grid)
        self.buttons = {}
        self.callbacks = {}
        for action, row, column in (("start", 0, 0), ("snooze", 0, 1), ("dismiss", 1, 0), ("off", 1, 1)):
            button = QPushButton()
            button.setObjectName(action)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            grid.addWidget(button, row, column)
            self.buttons[action] = button

    def configure(self, phase, effect, token, preview):
        self.phase, self.effect, self.token, self.preview = phase, effect, token, preview
        self.press_token = None
        interactive = effect.interactive
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, not interactive)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, not interactive)
        self.tomato.resting = phase == "break"
        self.tomato.setVisible(effect.style in ("bubble", "dim", "cover"))
        self.detail.setVisible(effect.style != "edge" or interactive)
        for action, button in self.buttons.items():
            if action in self.callbacks:
                button.clicked.disconnect(self.callbacks[action])
            button.setDown(False)
            callback = lambda _checked=False, name=action, generation=token: self.command.emit(generation, name)
            self.callbacks[action] = callback
            button.clicked.connect(callback)
            visible = interactive and (action in ("dismiss", "off") or phase == "waiting")
            if preview:
                visible = interactive and action == "dismiss"
            button.setVisible(visible)

    def set_text(self, message, detail, labels):
        self.title.setText(message)
        self.detail.setText(detail)
        for action, button in self.buttons.items():
            button.setText(labels[action])
        self.tomato.update()

    def place(self, screen, anchor):
        self.winId()
        handle = self.windowHandle()
        if handle.screen() != screen:
            handle.setScreen(screen)
        self.setGeometry(screen.geometry())
        area = screen.availableGeometry().translated(-screen.geometry().topLeft())
        style = self.effect.style
        width = min(500, area.width() - 32)
        if style in ("bubble", "edge"):
            width = min(360, width)
        if style == "banner":
            width = area.width() - 32
        self.panel.setFixedWidth(width)
        self.panel.adjustSize()
        if style in ("bubble", "edge"):
            point = anchor - screen.geometry().topLeft()
            x = point.x() - width // 2
            y = point.y() - self.panel.height() - 12
            if not screen.geometry().contains(anchor):
                x, y = area.right() - width - 16, area.bottom() - self.panel.height() - 16
        elif style == "banner":
            x, y = area.x() + 16, area.y() + 16
        else:
            x, y = area.center().x() - width // 2, area.center().y() - self.panel.height() // 2
        x = max(area.x() + 8, min(x, area.right() - width - 7))
        y = max(area.y() + 8, min(y, area.bottom() - self.panel.height() - 7))
        self.panel.move(x, y)
        self.panel.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_token = self.token

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton and self.effect.anywhere
                and self.press_token == self.token and self.effect.interactive):
            self.command.emit(self.token, "dismiss")
        self.press_token = None

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setOpacity(self.strength)
        bounds = QRectF(self.rect())
        if self.effect.interactive and self.effect.anywhere:
            painter.fillRect(bounds, QColor(0, 0, 0, 1))
        if self.effect.style == "dim":
            painter.fillRect(bounds, QColor(14, 24, 36, 95))
        elif self.effect.style == "cover":
            painter.fillRect(bounds, QColor("#1b283b"))
        elif self.effect.style == "edge":
            color = "#a4d9bc" if self.phase == "break" else "#f2ce91" if self.phase == "waiting" else "#75b9e9"
            painter.setPen(QPen(QColor(color), 3))
            painter.drawRect(bounds.adjusted(2, 2, -2, -2))
        painter.end()


class ScreenCues(QObject):
    action_requested = Signal(str)
    changed = Signal()

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.windows = {}
        self.phase = None
        self.message = ""
        self.detail = ""
        self.labels = {}
        self.effect = DEFAULTS["work"]
        self.preview = False
        self.generation = 0
        self.anchor = QPoint()
        self.animation = QVariantAnimation(self)
        self.animation.valueChanged.connect(self.update_strength)
        self.animation.finished.connect(self.finish_animation)
        app.screenAdded.connect(self.add_screen)
        app.screenRemoved.connect(self.remove_screen)
        for screen in app.screens():
            self.add_screen(screen)

    def add_screen(self, screen):
        screen.geometryChanged.connect(self.layout)
        screen.availableGeometryChanged.connect(self.layout)
        self.layout()

    def remove_screen(self, screen):
        window = self.windows.pop(screen, None)
        if window:
            window.hide()
            window.deleteLater()

    def layout(self, *_):
        if not self.phase:
            return
        for screen in self.app.screens():
            if screen not in self.windows:
                window = ScreenCue()
                window.command.connect(self.request_action)
                self.windows[screen] = window
                window.configure(self.phase, self.effect, self.generation, self.preview)
            window = self.windows[screen]
            window.set_text(self.message, self.detail, self.labels)
            window.strength = float(self.animation.currentValue() or 0)
            window.place(screen, self.anchor)
            window.show()
            window.update()

    def show(self, phase, effect, message, detail, labels, anchor, preview=False):
        self.clear()
        self.phase, self.effect, self.message = phase, effect, message
        self.detail, self.labels, self.anchor, self.preview = detail, labels, anchor, preview
        for window in self.windows.values():
            window.configure(phase, effect, self.generation, preview)
        self.animation.setDuration(effect.seconds * 1000 if effect.retention == "timed" else 220)
        self.animation.setStartValue(0.0)
        self.animation.setKeyValueAt(.12, 1.0)
        self.animation.setKeyValueAt(.75, 1.0)
        self.animation.setEndValue(0.0 if effect.retention == "timed" else 1.0)
        self.animation.setCurrentTime(0)
        self.layout()
        self.animation.start()
        self.changed.emit()

    def set_text(self, message, detail, labels):
        self.message, self.detail, self.labels = message, detail, labels
        self.layout()

    def update_strength(self, strength):
        for window in self.windows.values():
            window.strength = float(strength)
            window.update()

    def finish_animation(self):
        if self.effect.retention == "timed":
            self.clear()

    def request_action(self, token, action):
        if token != self.generation or self.phase is None:
            return
        if self.preview:
            self.clear()
        else:
            self.action_requested.emit(action)

    def clear(self):
        self.animation.stop()
        self.phase = None
        self.generation += 1
        for window in self.windows.values():
            window.press_token = None
            window.hide()
        self.changed.emit()

    def dispose(self):
        self.clear()
        self.app.screenAdded.disconnect(self.add_screen)
        self.app.screenRemoved.disconnect(self.remove_screen)
        for screen in self.app.screens():
            screen.geometryChanged.disconnect(self.layout)
            screen.availableGeometryChanged.disconnect(self.layout)
        for window in self.windows.values():
            window.close()
            window.deleteLater()
        self.windows.clear()
        self.deleteLater()
