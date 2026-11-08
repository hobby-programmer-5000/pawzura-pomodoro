"""MIT renderer for bounded vector-art data; artwork has its separate notice."""
from functools import lru_cache
from importlib.resources import files
import json
from math import isfinite, sin
import re

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen

from .classic import draw_classic


CHARACTERS = ("sprout", "classic")


def safe_character(value):
    return value if value in CHARACTERS else "sprout"


@lru_cache(maxsize=1)
def artwork():
    raw = files("pomodoro").joinpath("art/sprout-tomato-v1.json").read_bytes()
    if len(raw) > 100000:
        raise ValueError("Character asset too large")
    return validate_artwork(json.loads(raw))


def validate_artwork(data):
    """Accept only bounded drawing data, never executable paths or markup."""
    if not isinstance(data, dict) or type(data.get("schema")) is not int or data["schema"] != 1:
        raise ValueError("Invalid character schema")
    layers = data.get("layers")
    if not isinstance(layers, list) or not 1 <= len(layers) <= 64:
        raise ValueError("Invalid character layers")
    palette = data.get("palette", {})
    if not isinstance(palette, dict) or not 1 <= len(palette) <= 32 or any(
            not isinstance(k, str) or not isinstance(c, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", c)
            for k, c in palette.items()):
        raise ValueError("Invalid character colors")

    def number(value):
        if type(value) not in (int, float) or not isfinite(value) or not -100 <= value <= 240:
            raise ValueError("Invalid character coordinate")

    if not isinstance(data.get("gradient"), list) or len(data["gradient"]) != 4:
        raise ValueError("Invalid gradient")
    for v in data["gradient"]:
        number(v)
    for layer in data["layers"]:
        if not isinstance(layer, dict):
            raise ValueError("Invalid character layer")
        if not isinstance(layer.get("kind"), str) or layer["kind"] not in {"path", "ellipse", "line"}:
            raise ValueError("Invalid drawing primitive")
        if layer.get("role") is not None and (not isinstance(layer["role"], str) or layer["role"] not in {"eye", "left_foot", "right_foot", "left_arm", "right_arm"}):
            raise ValueError("Invalid drawing role")
        for key in ("fill", "stroke"):
            colors = layer.get(key)
            if colors is None:
                continue
            if isinstance(colors, str):
                colors = [colors]
            if (not isinstance(colors, list) or not 1 <= len(colors) <= (2 if key == "fill" else 1)
                    or any(not isinstance(c, str) or c not in palette for c in colors)):
                raise ValueError("Unknown character color")
            if key == "stroke" and not isinstance(layer[key], str):
                raise ValueError("Invalid stroke")
        if layer.get("role") == "eye" and not isinstance(layer.get("fill"), str):
            raise ValueError("Invalid eye color")
        width = layer.get("width", 0)
        number(width)
        if not 0 <= width <= 10:
            raise ValueError("Invalid line width")
        left, right = layer.get("standing"), layer.get("seated")
        if not isinstance(left, list) or not isinstance(right, list) or len(left) != len(right):
            raise ValueError("Pose topology differs")
        if layer["kind"] == "path":
            if not 1 <= len(left) <= 64:
                raise ValueError("Invalid path size")
            for a, b in zip(left, right):
                if (not isinstance(a, list) or not isinstance(b, list) or not a or not b
                        or not isinstance(a[0], str) or a[0] not in {"M", "L", "C", "Z"} or a[0] != b[0]):
                    raise ValueError("Invalid path command")
                length = {"M": 3, "L": 3, "C": 7, "Z": 1}[a[0]]
                if len(a) != length or len(b) != length:
                    raise ValueError("Invalid path coordinates")
                for v in (*a[1:], *b[1:]):
                    number(v)
            if left[0][0] != "M":
                raise ValueError("Path must start with a move")
        else:
            if len(left) != 4:
                raise ValueError("Invalid primitive bounds")
            for v in (*left, *right):
                number(v)
            if layer["kind"] == "ellipse" and any(v < 0 for v in (*left[2:], *right[2:])):
                raise ValueError("Negative ellipse size")
    return data


def blend(a, b, amount):
    return [x + (y - x) * amount for x, y in zip(a, b)]


def draw_tomato(painter, phase=0.0, direction=1, walking=False, resting=False, reaction=None, seated=None, character="sprout"):
    seated = float(resting) if seated is None else max(0.0, min(1.0, seated))
    if character == "classic":
        return draw_classic(painter, phase, direction, walking, resting, reaction, seated)
    data = artwork()
    walking = walking and seated == 0
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(72, 0)
    painter.scale(direction, 1)
    painter.translate(-72, -abs(sin(phase)) * 2.5 if walking else 0)
    for layer in data["layers"]:
        painter.save()
        role = layer.get("role")
        if walking and role in ("left_foot", "right_foot"):
            sign = 1 if role == "left_foot" else -1
            painter.translate(sign * sin(phase) * 7, -max(0, sign * sin(phase)) * 4)
        if reaction and seated == 0 and role in ("left_arm", "right_arm"):
            painter.translate(0, -8 * abs(sin(phase)) if reaction == "wave" else -7 if reaction == "cheer" else 0)
        stroke = layer.get("stroke")
        painter.setPen(QPen(QColor(data["palette"][stroke]), layer.get("width", 1), Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin) if stroke else Qt.PenStyle.NoPen)
        fill = layer.get("fill")
        if isinstance(fill, list):
            gradient = QLinearGradient(*data["gradient"])
            gradient.setColorAt(0, QColor(data["palette"][fill[0]]))
            gradient.setColorAt(1, QColor(data["palette"][fill[-1]]))
            painter.setBrush(gradient)
        else:
            painter.setBrush(QColor(data["palette"][fill]) if fill else Qt.BrushStyle.NoBrush)
        if layer["kind"] == "path":
            path = QPainterPath()
            for a, b in zip(layer["standing"], layer["seated"]):
                coords = blend(a[1:], b[1:], seated)
                if a[0] == "M": path.moveTo(*coords)
                elif a[0] == "L": path.lineTo(*coords)
                elif a[0] == "C": path.cubicTo(*coords)
                else: path.closeSubpath()
            painter.drawPath(path)
        else:
            values = blend(layer["standing"], layer["seated"], seated)
            if role == "eye" and resting and seated >= .5:
                x, y, w, h = values
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(QColor(data["palette"][fill]), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                painter.drawArc(QRectF(x - 1, y + h * .15, w + 2, h * .7), 180 * 16, 180 * 16)
            elif layer["kind"] == "ellipse":
                painter.drawEllipse(QRectF(*values))
            else:
                painter.drawLine(QPointF(*values[:2]), QPointF(*values[2:]))
        painter.restore()
    painter.restore()
