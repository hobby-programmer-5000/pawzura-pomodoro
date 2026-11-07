from math import cos, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton

from pawzura.pet import Pet


def draw_tomato(painter, phase=0.0, direction=1, walking=False, resting=False, reaction=None):
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(72, 0)
    painter.scale(direction, 1)
    painter.translate(-72, -abs(sin(phase)) * 3 if walking else 0)

    outline = QColor("#682f30")
    no_pen = Qt.PenStyle.NoPen
    solid = Qt.PenStyle.SolidLine
    round_cap = Qt.PenCapStyle.RoundCap
    painter.setPen(QPen(outline, 6, solid, round_cap))
    step = sin(phase) * 9 if walking else 0
    lift = cos(phase) * 5 if walking else 0
    left_lift, right_lift = max(0, lift), max(0, -lift)
    painter.drawLine(QPointF(53, 116), QPointF(50 + step, 131 - left_lift))
    painter.drawLine(QPointF(90, 116), QPointF(90 - step, 131 - right_lift))
    painter.setPen(no_pen)
    painter.setBrush(outline)
    painter.drawEllipse(QRectF(40 + step, 127 - left_lift, 23, 11))
    painter.drawEllipse(QRectF(80 - step, 127 - right_lift, 23, 11))

    painter.setPen(QPen(outline, 6, solid, round_cap))
    wave = sin(phase * 2) * 7 if reaction == "wave" else 0
    painter.drawLine(QPointF(28, 87), QPointF(16, 73 if reaction == "cheer" else 97))
    painter.drawLine(QPointF(115, 87), QPointF(130, 69 + wave if reaction in ("wave", "cheer") else 96))

    tomato = QPainterPath(QPointF(72, 48))
    tomato.cubicTo(42, 32, 20, 54, 20, 82)
    tomato.cubicTo(20, 111, 44, 127, 72, 125)
    tomato.cubicTo(102, 127, 124, 110, 124, 82)
    tomato.cubicTo(124, 54, 102, 33, 72, 48)
    tomato.closeSubpath()
    skin = QLinearGradient(34, 45, 105, 123)
    skin.setColorAt(0, QColor("#ff8c6b"))
    skin.setColorAt(0.52, QColor("#f35d4c"))
    skin.setColorAt(1, QColor("#d64140"))
    painter.setPen(QPen(outline, 3))
    painter.setBrush(skin)
    painter.drawPath(tomato)
    painter.setPen(no_pen)
    painter.setBrush(QColor("#ffb496"))
    painter.drawEllipse(QRectF(32, 63, 9, 16))

    cap = QPainterPath(QPointF(67, 44))
    cap.cubicTo(56, 31, 43, 32, 37, 37)
    cap.cubicTo(45, 48, 56, 49, 62, 48)
    cap.cubicTo(54, 53, 52, 57, 52, 62)
    cap.cubicTo(66, 62, 74, 56, 77, 50)
    cap.cubicTo(87, 57, 96, 54, 105, 49)
    cap.cubicTo(98, 39, 88, 37, 76, 42)
    cap.cubicTo(75, 35, 77, 30, 82, 28)
    cap.cubicTo(80, 24, 77, 24, 73, 26)
    cap.cubicTo(67, 30, 66, 37, 67, 44)
    cap.closeSubpath()
    painter.setPen(QPen(QColor("#244639"), 2.5))
    painter.setBrush(QColor("#6cbe77"))
    painter.drawPath(cap)

    painter.setPen(no_pen)
    painter.setBrush(QColor("#ff9c90"))
    painter.drawEllipse(QRectF(40, 92, 14, 7))
    painter.drawEllipse(QRectF(92, 92, 14, 7))
    face = QColor("#45232b")
    painter.setBrush(face)
    for x in (59, 88):
        if resting:
            painter.setPen(QPen(face, 2.8, solid, round_cap))
            painter.drawArc(QRectF(x - 5, 79, 10, 10), 180 * 16, 180 * 16)
        else:
            painter.drawEllipse(QRectF(x - 3.5, 76, 7, 12))
    painter.setPen(QPen(face, 3, solid, round_cap))
    painter.drawArc(QRectF(67, 88, 13, 12), 180 * 16, 180 * 16)
    painter.restore()


class TimerPet(Pet):
    def __init__(self, language, direction):
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

    def set_countdown(self, text, action, resting):
        self.resting = resting
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
        walking = not (self.pinned or self.pointer_active or self.hovered or self.reaction)
        draw_tomato(
            painter, self.phase, self.look_direction if self.hovered else self.direction,
            walking, self.resting, self.reaction["kind"] if self.reaction else None,
        )
        painter.end()

    def contextMenuEvent(self, event):
        if self.menu:
            self.menu.popup(event.globalPos())
        event.accept()

    def screen_changed(self, *_):
        self.reset_pointer()
        self.set_placement(self.pinned, self.resting_position())
