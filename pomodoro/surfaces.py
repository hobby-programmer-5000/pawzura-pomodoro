from time import monotonic

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QPushButton

from pawzura.pet import Pet

from .character import draw_tomato
from .posture import Posture


class TimerPet(Pet):
    def __init__(self, language, direction, pose_clock=None, character="sprout"):
        self.posture = Posture(pose_clock)
        self.character = character
        super().__init__(None, language, direction)
        self.resting = False
        self.setWindowTitle("Pawzura Pomodoro")
        self.badge = QPushButton(self)
        self.badge.setMaximumWidth(self.width() - 2)
        self.badge.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.badge.setStyleSheet("""
            QPushButton {
                background: #22283a;
                color: #f4f8ff;
                border: 1px solid #75849f;
                border-radius: 10px;
                padding: 2px 9px;
                font-weight: 600;
            }
            QPushButton:hover { background: #343e54; }
        """)
        self.menu = None

    def set_phase(self, phase):
        if self.posture.phase == phase:
            return
        self.posture.set_phase(phase)
        self.resting = phase == "break"
        if self.posture.stationary:
            self.reaction = None
            self.cancel_bite(recover=False, reset_pointer=False)
        self.update()

    def tick(self):
        self.posture.update()
        if self.posture.stationary:
            self.last_tick = monotonic()
            self.reaction = None
            self.update()
            return
        super().tick()

    def react(self, kind):
        if self.posture.stationary:
            return False
        return super().react(kind)

    def set_countdown(self, text, action):
        label, separator, time = text.rpartition(" · ")
        metrics = self.badge.fontMetrics()
        available = self.width() - 24 - metrics.horizontalAdvance(separator + time)
        short_label = metrics.elidedText(label, Qt.TextElideMode.ElideRight, max(0, available))
        display = short_label + separator + time if short_label else time
        if self.badge.text() != display:
            self.badge.setText(display)
            self.badge.adjustSize()
            self.badge.move((self.width() - self.badge.width()) // 2, 0)
        self.badge.setToolTip(f"{text}\n{action}")
        self.badge.setAccessibleName(f"{text} · {action}")

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        walking = not (self.posture.stationary or self.pinned or self.pointer_active or self.hovered or self.reaction)
        draw_tomato(
            painter, self.phase, self.look_direction if self.hovered and not self.posture.stationary else self.direction,
            walking, self.resting, self.reaction["kind"] if self.reaction else None, self.posture.amount, self.character,
        )
        painter.end()

    def contextMenuEvent(self, event):
        if self.menu:
            self.menu.popup(event.globalPos())
        event.accept()

    def screen_changed(self, *_):
        self.reset_pointer()
        self.set_placement(self.pinned, self.resting_position())
