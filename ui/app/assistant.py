import json
import copy
import time
from pathlib import Path
import traceback

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QPushButton,
    QSystemTrayIcon,
    QMenu,
    QLabel,
    QScrollArea,
    QMessageBox,
)
from PyQt6.QtCore import (
    Qt,
    QSize,
)
from PyQt6.QtGui import (
    QIcon,
    QShortcut,
    QKeySequence,
)

from .custom_plaintext_editor import CustomPlainTextEdit
from .icons import (
    create_icon_from_svg,
    microphone_icon_svg,
    copy_icon_svg,
    clear_icon_svg,
)

class Assistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('AI assistant')
        self.setFixedSize(600, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.image_layout = QHBoxLayout()
        self.image_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(self.image_layout)

        top_layout = QHBoxLayout()

        self.input_field = CustomPlainTextEdit(self.on_submit, self)
        self.input_field.setPlaceholderText('Ask me anything...')
        self.input_field.setAcceptDrops(True)
        self.input_field.setFixedHeight(100)
        self.input_field.dragEnterEvent = self.dragEnterEvent
        self.input_field.dropEvent = self.dropEvent
        self.input_field.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 16px;
                height: 40px;
            }
            """
        )
        top_layout.addWidget(self.input_field)

        self.mic_button = QPushButton(self)
        self.mic_button.setIcon(create_icon_from_svg(microphone_icon_svg))
        self.mic_button.setIconSize(QSize(24, 24))
        self.mic_button.setFixedSize(40, 40)
        self.mic_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius: 20px;
                background-color: rgba(100, 100, 100, 200);
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 230);
            }
            """
        )
        # self.mic_button.clicked.connect(self.toggle_voice_input)
        top_layout.addWidget(self.mic_button)

        close_button = QPushButton('X', self)
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 0, 0, 150);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 5px;
                font-size: 20px;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 200);
            }
            """
        )
        close_button.clicked.connect(self.hide)
        top_layout.addWidget(close_button)

        main_layout.addLayout(top_layout)
        
        # add new buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.summarize_button = QPushButton('Summarize', self)
        self.repharse_button = QPushButton('Repharse', self)
        self.fix_grammar_button = QPushButton('Fix Grammar', self)
        self.brainstorm_button = QPushButton('Brainstorm', self)
        self.write_email_button = QPushButton('Write Email', self)

        # add new buttons to layout
        result_layout = QHBoxLayout()
        result_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Create and set up the Copy Result button
        self.copy_button = QPushButton("Copy Result", self)
        self.copy_button.setIcon(create_icon_from_svg(copy_icon_svg))
        self.copy_button.setIconSize(QSize(18, 18))
        self.copy_button.setStyleSheet(
            """
            QPushButton {
                padding-left: 4px;
                padding-right: 8px;
            }
            QPushButton:icon {
            margin-right: 4px;
            }
            """
        )
        # self.copy_button.clicked.connect(self.copy_result)
        # self.copy_button.hide()

        # Create and set up the Clear Result button
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setIcon(create_icon_from_svg(clear_icon_svg))
        self.clear_button.setIconSize(QSize(18, 18))
        self.clear_button.setStyleSheet(
            """
            QPushButton {
                padding-left: 4px;
                padding-right: 8px;
            }
            QPushButton:icon {
                margin-right: 4px;
            }
            """
        )
        # self.clear_button.clicked.connect(self.clear_chat)
        # self.clear_button.hide()

        result_layout.addWidget(self.copy_button)
        result_layout.addWidget(self.clear_button)

        for button in [
            self.summarize_button,
            self.repharse_button,
            self.fix_grammar_button,
            self.brainstorm_button,
            self.write_email_button,
        ]:
            button_style = """
                QPushButton {
                    color: white;
                    padding: 2.5px 5px;
                    border-radius: 5px;
                    background-color: rgba(0, 0, 0, 200);
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 200);
                }
            """
            button.setStyleSheet(button_style)
            # button.clicked.connect(self.on_task_button_clicked)
            button_layout.addWidget(button)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(result_layout)

        # Create a scroll area for the chat box
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 200);
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 230);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            """
        )
        self.chat_box = QTextBrowser(self.scroll_area)
        self.chat_box.setOpenExternalLinks(True)
        self.scroll_area.setWidget(self.chat_box)
        self.scroll_area.hide()
        main_layout.addWidget(self.scroll_area)

        self.esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.esc_shortcut.activated.connect(self.hide)



    def on_submit(self):
        pass