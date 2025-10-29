import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDialog
from PyQt6.QtCore import Qt, QSettings

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setObjectName("settings_dialog")

        self.settings = QSettings("PomodoroFlow", "AppSettings")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Time settings
        self.focus_time_input = self.create_setting_input("🍅 Focus Time (min):", self.settings.value("focus_time", 25, type=int))
        self.short_break_input = self.create_setting_input("☕️ Short Break (min):", self.settings.value("short_break_time", 5, type=int))
        self.long_break_input = self.create_setting_input("🎉 Long Break (min):", self.settings.value("long_break_time", 15, type=int))
        self.long_break_interval_input = self.create_setting_input("🔄 Interval:", self.settings.value("long_break_interval", 4, type=int))

        layout.addLayout(self.focus_time_input["layout"])
        layout.addLayout(self.short_break_input["layout"])
        layout.addLayout(self.long_break_input["layout"])
        layout.addLayout(self.long_break_interval_input["layout"])

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_setting_input(self, label_text, value):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        spinbox = QSpinBox()
        spinbox.setMinimum(1)
        spinbox.setMaximum(120)
        spinbox.setValue(value)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(spinbox)
        return {"layout": layout, "input": spinbox}

    def save_settings(self):
        self.settings.setValue("focus_time", self.focus_time_input["input"].value())
        self.settings.setValue("short_break_time", self.short_break_input["input"].value())
        self.settings.setValue("long_break_time", self.long_break_input["input"].value())
        self.settings.setValue("long_break_interval", self.long_break_interval_input["input"].value())
        self.accept()
