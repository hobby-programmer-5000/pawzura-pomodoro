from PySide6.QtCore import QSettings, QSignalBlocker, Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from .effects import EVENTS, STYLES, retention_choices
from .timer import MAX_MINUTES


class EffectOptions(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.labels = {}
        form = QFormLayout(self)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.event = QComboBox()
        for event in EVENTS:
            self.event.addItem("", event)
        self.event.setCurrentIndex(2)
        self.event.activated.connect(self.refresh)
        self.add_field(form, "cue_event", self.event)
        self.style = QComboBox()
        for style in STYLES:
            self.style.addItem("", style)
        self.style.activated.connect(self.save_effect)
        self.add_field(form, "cue_style", self.style)
        self.retention = QComboBox()
        self.retention.activated.connect(self.save_effect)
        self.add_field(form, "cue_retention", self.retention)
        self.seconds = QSpinBox()
        self.seconds.setRange(1, 60)
        self.seconds.setKeyboardTracking(False)
        self.seconds.valueChanged.connect(self.save_effect)
        self.add_field(form, "cue_seconds", self.seconds)
        self.anywhere = QCheckBox()
        self.anywhere.clicked.connect(self.save_effect)
        form.addRow(self.anywhere)
        self.snooze = QSpinBox()
        self.snooze.setRange(1, 30)
        self.snooze.setKeyboardTracking(False)
        self.snooze.valueChanged.connect(controller.set_snooze)
        self.add_field(form, "snooze_minutes", self.snooze)
        self.help = QLabel()
        self.help.setWordWrap(True)
        form.addRow(self.help)
        self.preview = QPushButton()
        self.preview.clicked.connect(lambda: controller.preview_effect(self.event.currentData()))
        form.addRow(self.preview)

    def add_field(self, form, key, widget):
        label = QLabel()
        label.setBuddy(widget)
        form.addRow(label, widget)
        self.labels[key] = label

    def refresh(self, *_):
        owner, event = self.controller, self.event.currentData()
        text, effect = owner.text, owner.cue_settings[event]
        for key, label in self.labels.items():
            label.setText(text[key])
        for index, value in enumerate(EVENTS):
            self.event.setItemText(index, text[f"event_{value}"])
        for index, value in enumerate(STYLES):
            self.style.setItemText(index, text[f"style_{value}"])
        self.style.setCurrentIndex(self.style.findData(effect.style))
        self.retention.clear()
        for value in retention_choices(event):
            self.retention.addItem(text[f"retention_{value}"], value)
        self.retention.setCurrentIndex(self.retention.findData(effect.retention))
        with QSignalBlocker(self.seconds), QSignalBlocker(self.snooze):
            self.seconds.setValue(effect.seconds)
            self.snooze.setValue(owner.snooze_minutes)
        self.seconds.setEnabled(effect.retention == "timed")
        self.anywhere.setText(text["cue_anywhere"])
        self.anywhere.setChecked(effect.anywhere)
        self.anywhere.setEnabled(effect.interactive)
        self.help.setText(text["effects_help"])
        self.preview.setText(text["preview_effect"])

    def save_effect(self, *_):
        self.controller.set_cue(
            self.event.currentData(), self.style.currentData(), self.retention.currentData(),
            self.seconds.value(), self.anywhere.isChecked(),
        )


class Options(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        self.status = QLabel()
        status_font = self.status.font()
        status_font.setPointSize(15)
        status_font.setBold(True)
        self.status.setFont(status_font)
        layout.addWidget(self.status)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        general = QWidget()
        general_layout = QVBoxLayout(general)
        form = QFormLayout()
        general_layout.addLayout(form)
        self.fields = {}

        self.language = QComboBox()
        self.language.addItem("English", "en")
        self.language.addItem("한국어", "ko")
        self.language.activated.connect(lambda _: controller.set_language(self.language.currentData()))
        self.add_field(form, "language", self.language)
        for key, value, callback in (
            ("work_minutes", controller.timer.work, controller.set_work),
            ("rest_minutes", controller.timer.rest, controller.set_rest),
        ):
            spin = QSpinBox()
            spin.setRange(1, MAX_MINUTES)
            spin.setValue(value)
            spin.setKeyboardTracking(False)
            spin.valueChanged.connect(callback)
            self.add_field(form, key, spin)
        self.effects = QCheckBox()
        self.effects.clicked.connect(controller.set_effects)
        form.addRow(self.effects)
        self.walking = QCheckBox()
        self.walking.clicked.connect(controller.set_walking)
        form.addRow(self.walking)
        self.direction = QComboBox()
        self.direction.addItems(["", ""])
        self.direction.activated.connect(lambda index: controller.set_direction(("left", "right")[index]))
        self.add_field(form, "direction", self.direction)
        self.help = QLabel()
        self.help.setWordWrap(True)
        general_layout.addWidget(self.help)
        general_layout.addStretch()
        self.tabs.addTab(general, "")
        self.effect_options = EffectOptions(controller)
        self.tabs.addTab(self.effect_options, "")
        self.save_status = QLabel()
        self.save_status.setWordWrap(True)
        layout.addWidget(self.save_status)
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        self.toggle = QPushButton()
        self.toggle.clicked.connect(controller.toggle)
        buttons.addWidget(self.toggle)
        self.reset = QPushButton()
        self.reset.clicked.connect(controller.reset)
        buttons.addWidget(self.reset)
        buttons.addStretch()
        self.close_button = QPushButton()
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.close_button)
        for button in (self.toggle, self.reset, self.close_button):
            button.setAutoDefault(False)

    def add_field(self, form, key, widget):
        label = QLabel()
        label.setBuddy(widget)
        form.addRow(label, widget)
        self.fields[key] = label

    def refresh(self):
        owner, text = self.controller, self.controller.text
        self.setWindowTitle(f"Pawzura Pomodoro · {text['options']}")
        for key, label in self.fields.items():
            label.setText(text[key])
        self.language.setCurrentIndex(self.language.findData(owner.language))
        self.effects.setText(text["effects"])
        self.effects.setChecked(owner.effects)
        self.walking.setText(text["walking"])
        self.walking.setChecked(owner.walking)
        self.direction.setItemText(0, text["left"])
        self.direction.setItemText(1, text["right"])
        self.direction.setCurrentIndex(int(owner.direction == "right"))
        self.help.setText(text["help"])
        self.save_status.setText(text["save_error"])
        self.save_status.setVisible(owner.store.status() != QSettings.Status.NoError)
        self.reset.setText(text["reset"])
        self.close_button.setText(text["close"])
        self.tabs.setTabText(0, text["general_tab"])
        self.tabs.setTabText(1, text["effects_tab"])
        self.effect_options.refresh()
        self.update_timer(owner.countdown(), owner.toggle_label())

    def update_timer(self, countdown, action):
        self.status.setText(countdown)
        self.toggle.setText(action)
        self.reset.setEnabled(self.controller.timer.phase != "ready")
