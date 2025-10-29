
def get_styles():
    return """
        QWidget {
            background-color: #fdf6e3; /* A soft, creamy background */
            color: #657b83; /* A gentle, dark gray for text */
            font-family: 'Comic Sans MS', 'Chalkboard SE', 'Marker Felt', sans-serif;
        }

        QPushButton {
            background-color: #eee8d5; /* A slightly darker cream for buttons */
            border: 1px solid #d3cbb7;
            border-radius: 15px; /* Rounded corners */
            padding: 10px 15px;
            font-size: 16px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #d3cbb7; /* Darken on hover */
        }

        QPushButton:pressed {
            background-color: #b58900; /* A warm, golden color for pressed state */
            color: #fdf6e3;
        }

        QLabel#timer_display {
            font-size: 70px;
            font-weight: bold;
            color: #586e75; /* A slightly darker, more prominent color */
        }

        QLabel#stage_label {
            font-size: 24px;
            font-weight: bold;
            color: #b58900; /* Golden color for the stage */
            margin-bottom: 10px;
        }

        QLabel#pomodoro_counter {
            font-size: 18px;
            color: #859900; /* A gentle green */
        }
        
        QDialog {
            background-color: #fdf6e3;
        }
        
        QSpinBox {
            padding: 5px;
            border: 1px solid #d3cbb7;
            border-radius: 5px;
        }
    """

FOCUS_COLOR = "#ff7979"  # A soft, cute red/pink
BREAK_COLOR = "#badc58"    # A gentle, minty green
