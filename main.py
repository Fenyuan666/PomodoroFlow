
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtCore import QTimer, Qt, QSettings, QPointF
from PyQt6.QtGui import QFont, QIcon, QPainter, QColor, QBrush, QPen
import os
from settings import SettingsWindow

class CircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 1.0
        self.focus_color = QColor("#e74c3c")
        self.break_color = QColor("#2ecc71")
        self.current_color = self.focus_color

    def set_progress(self, progress):
        self.progress = progress
        self.update()

    def set_color(self, color):
        self.current_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height())
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#f0f0f0"))
        painter.drawEllipse(rect)

        painter.setBrush(self.current_color)
        
        start_angle = 90 * 16
        span_angle = -int(self.progress * 360 * 16)
        
        painter.drawPie(rect, start_angle, span_angle)


class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Flow")
        self.setFixedSize(400, 500)

        self.settings = QSettings("PomodoroFlow", "AppSettings")
        self.load_settings()

        self.current_stage = "focus"
        self.pomodoros_completed = 0
        self.is_paused = False

        self.time_left = self.focus_time * 60
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()
        self.update_colors()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Timer display
        timer_layout = QGridLayout()
        self.circular_timer = CircularTimer()
        self.timer_display = QLabel(self.format_time(self.time_left))
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        
        timer_layout.addWidget(self.circular_timer, 0, 0)
        timer_layout.addWidget(self.timer_display, 0, 0)


        # Stage label
        self.stage_label = QLabel(self.get_stage_text())
        self.stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stage_label.setFont(QFont("Arial", 20))

        # Pomodoro counter
        self.pomodoro_counter = QLabel(f"🍅 {self.pomodoros_completed} / {self.long_break_interval}")
        self.pomodoro_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pomodoro_counter.setFont(QFont("Arial", 16))

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        
        self.settings_button = QPushButton("⚙️")
        self.settings_button.clicked.connect(self.open_settings)


        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.reset_button)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 10, 0, 0)
        top_layout.addStretch()
        top_layout.addWidget(self.settings_button)


        main_layout.addLayout(top_layout)
        main_layout.addLayout(timer_layout)
        main_layout.addWidget(self.stage_label)
        main_layout.addWidget(self.pomodoro_counter)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def get_stage_text(self):
        if self.current_stage == "focus":
            return "Focus Work"
        elif self.current_stage == "short_break":
            return "Short Break"
        elif self.current_stage == "long_break":
            return "Long Break"

    def update_timer(self):
        if not self.is_paused:
            self.time_left -= 1
            self.update_ui()
            if self.time_left < 0:
                self.timer.stop()
                self.next_stage()

    def start_timer(self):
        if self.timer.isActive() and not self.is_paused:
            self.is_paused = True
            self.timer.stop()
            self.start_button.setText("Continue")
        else:
            self.is_paused = False
            self.timer.start(1000)
            self.start_button.setText("Pause")

    def reset_timer(self):
        self.timer.stop()
        self.is_paused = False
        self.current_stage = "focus"
        self.pomodoros_completed = 0
        self.time_left = self.focus_time * 60
        self.update_ui()
        self.start_button.setText("Start")
        self.update_colors()


    def next_stage(self):
        if self.current_stage == "focus":
            self.pomodoros_completed += 1
            if self.pomodoros_completed % self.long_break_interval == 0:
                self.current_stage = "long_break"
                self.time_left = self.long_break_time * 60
            else:
                self.current_stage = "short_break"
                self.time_left = self.short_break_time * 60
        elif self.current_stage in ["short_break", "long_break"]:
            self.current_stage = "focus"
            self.time_left = self.focus_time * 60
        
        self.update_ui()
        self.update_colors()
        self.send_notification()
        self.timer.start(1000)

    def update_ui(self):
        total_time = self.get_current_stage_duration()
        progress = self.time_left / total_time
        self.circular_timer.set_progress(progress)
        self.timer_display.setText(self.format_time(self.time_left))
        self.stage_label.setText(self.get_stage_text())
        self.pomodoro_counter.setText(f"🍅 {self.pomodoros_completed % self.long_break_interval} / {self.long_break_interval}")

    def update_colors(self):
        if self.current_stage == "focus":
            self.circular_timer.set_color(QColor("#e74c3c"))
        else:
            self.circular_timer.set_color(QColor("#2ecc71"))

    def get_current_stage_duration(self):
        if self.current_stage == "focus":
            return self.focus_time * 60
        elif self.current_stage == "short_break":
            return self.short_break_time * 60
        else:
            return self.long_break_time * 60

    def send_notification(self):
        message = f"Time for {self.get_stage_text()}!"
        os.system(f'osascript -e \'display notification "{message}" with title "Pomodoro Flow"\'')

    def open_settings(self):
        settings_dialog = SettingsWindow(self)
        if settings_dialog.exec():
            self.load_settings()
            self.reset_timer()
            
    def load_settings(self):
        self.focus_time = self.settings.value("focus_time", 25, type=int)
        self.short_break_time = self.settings.value("short_break_time", 5, type=int)
        self.long_break_time = self.settings.value("long_break_time", 15, type=int)
        self.long_break_interval = self.settings.value("long_break_interval", 4, type=int)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroApp()
    window.show()
    sys.exit(app.exec())
