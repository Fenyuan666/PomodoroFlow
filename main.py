
class PulsingCircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 1.0
        self.current_color = QColor(FOCUS_COLOR)
        self._scale = 1.0 # Internal scale variable

        self.animation = QPropertyAnimation(self, b"scale") # Animate the registered 'scale' property
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(1.02)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1) # Loop indefinitely

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self.update()

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
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 * self._scale
        
        draw_rect = QRect(int(center.x() - radius), int(center.y() - radius), int(radius * 2), int(radius * 2))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#eee8d5"))
        painter.drawEllipse(draw_rect)

        painter.setBrush(self.current_color)
        
        start_angle = 90 * 16
        span_angle = -int(self.progress * 360 * 16)
        
        painter.drawPie(draw_rect, start_angle, span_angle)


class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Flow")
        self.setFixedSize(400, 530)
        self.setWindowIcon(QIcon("🍅"))

        self.settings = QSettings("PomodoroFlow", "AppSettings")
        self.load_settings()

        self.current_stage = "focus"
        self.pomodoros_completed = 0
        self.is_paused = True # Start paused

        self.time_left = self.focus_time * 60
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()
        self.update_colors()
        self.update_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Timer display
        timer_layout = QGridLayout()
        self.circular_timer = PulsingCircularTimer()
        self.timer_display = QLabel(self.format_time(self.time_left))
        self.timer_display.setObjectName("timer_display")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        timer_layout.addWidget(self.circular_timer, 0, 0)
        timer_layout.addWidget(self.timer_display, 0, 0)


        # Stage label
        self.stage_label = QLabel(self.get_stage_text())
        self.stage_label.setObjectName("stage_label")
        self.stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Pomodoro counter
        self.pomodoro_counter = QLabel()
        self.pomodoro_counter.setObjectName("pomodoro_counter")
        self.pomodoro_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedWidth(50)
        self.settings_button.clicked.connect(self.open_settings)


        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.reset_button)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.settings_button)


        main_layout.addLayout(top_layout)
        main_layout.addLayout(timer_layout, 1) # Give the timer layout more space
        main_layout.addWidget(self.stage_label)
        main_layout.addWidget(self.pomodoro_counter)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def get_stage_text(self):
        if self.current_stage == "focus":
            return "🍅 Focus Time 🍅"
        elif self.current_stage == "short_break":
            return "☕️ Short Break ☕️"
        elif self.current_stage == "long_break":
            return "🎉 Long Break 🎉"

    def update_timer(self):
        if not self.is_paused:
            self.time_left -= 1
            self.update_ui()
            if self.time_left < 0:
                self.timer.stop()
                self.next_stage()

    def start_timer(self):
        if self.is_paused:
            self.is_paused = False
            self.timer.start(1000)
            self.circular_timer.animation.start() # Start animation when timer starts
            self.start_button.setText("Pause")
        else:
            self.is_paused = True
            self.timer.stop()
            self.circular_timer.animation.pause()
            self.start_button.setText("Continue")

    def reset_timer(self):
        self.timer.stop()
        self.is_paused = True
        self.current_stage = "focus"
        self.pomodoros_completed = 0
        self.time_left = self.focus_time * 60
        self.update_ui()
        self.start_button.setText("Start")
        self.update_colors()
        self.circular_timer.animation.stop() # Stop animation on reset


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
        
        self.is_paused = True
        self.start_button.setText("Start")
        self.update_ui()
        self.update_colors()
        self.send_notification()
        self.circular_timer.animation.stop() # Stop animation when stage changes, will be started again by start_timer

    def update_ui(self):
        total_time = self.get_current_stage_duration()
        if total_time > 0:
            progress = self.time_left / total_time
            self.circular_timer.set_progress(progress)
        
        self.timer_display.setText(self.format_time(self.time_left))
        self.stage_label.setText(self.get_stage_text())
        
        pomodoros_to_show = self.pomodoros_completed % self.long_break_interval
        if self.pomodoros_completed > 0 and pomodoros_to_show == 0 and self.current_stage != 'focus':
            pomodoros_to_show = self.long_break_interval
            
        self.pomodoro_counter.setText("🍅" * pomodoros_to_show + "🤍" * (self.long_break_interval - pomodoros_to_show))


    def update_colors(self):
        if self.current_stage == "focus":
            self.circular_timer.set_color(QColor(FOCUS_COLOR))
        else:
            self.circular_timer.set_color(QColor(BREAK_COLOR))

    def get_current_stage_duration(self):
        if self.current_stage == "focus":
            return self.focus_time * 60
        elif self.current_stage == "short_break":
            return self.short_break_time * 60
        else:
            return self.long_break_time * 60

    def send_notification(self):
        message = f"Time for {self.get_stage_text()}!"
        os.system(f'osascript -e \'display notification "{message}" with title "Pomodoro Flow" sound name "Submarine"\'')

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
    app.setStyleSheet(get_styles())
    window = PomodoroApp()
    window.show()
    sys.exit(app.exec())
