from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class AlgorithmsWindow(QWidget):
    def __init__(self, user, on_navigate, on_select_algorithm):
        super().__init__()
        self.user = user
        self.on_navigate = on_navigate
        self.on_select_algorithm = on_select_algorithm
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cryptography Toolkit - Algorithms")
        self.setGeometry(100, 100, 1000, 700)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
            #sidebar {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                                                 stop:0 rgba(87, 108, 188, 255),
                                                 stop:1 rgba(69, 88, 158, 255));
            }
        """)
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(20)

        back_button = QPushButton("←")
        back_button.setFont(QFont("Arial", 24, QFont.Bold))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        back_button.setFixedHeight(50)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(lambda: self.on_navigate("home"))

        sidebar_layout.addWidget(back_button)
        sidebar_layout.addSpacing(30)

        messages_button = self.create_sidebar_button("📧 Messages", "messages")
        algos_button = self.create_sidebar_button("🧠 Algorithmes\nde Cryptage", "algorithms")
        attacks_button = self.create_sidebar_button("⚔️ Attaques", "attacks")

        sidebar_layout.addWidget(messages_button)
        sidebar_layout.addWidget(algos_button)
        sidebar_layout.addWidget(attacks_button)
        sidebar_layout.addStretch()

        content = QWidget()
        content.setStyleSheet("background-color: #f5f7fa;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setAlignment(Qt.AlignTop)

        title = QLabel("Choisissez un algorithme de cryptage")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: #0d214f;")
        title.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(title)
        content_layout.addSpacing(50)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(30)
        grid_layout.setAlignment(Qt.AlignCenter)

        algorithms = [
            ("Ceasar", "ceasar"),
            ("PlayFair", "playfair"),
            ("Affine", "affine"),
            ("Hill", "hill")
        ]

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for (name, algo_key), (row, col) in zip(algorithms, positions):
            button = self.create_algorithm_button(name, algo_key)
            grid_layout.addWidget(button, row, col)

        content_layout.addLayout(grid_layout)
        content_layout.addStretch()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

    def create_sidebar_button(self, text, page):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 14, QFont.Bold))
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        button.setFixedHeight(80)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self.on_navigate(page))
        return button

    def create_algorithm_button(self, name, algo_key):
        button = QPushButton(name)
        button.setFont(QFont("Arial", 18, QFont.Bold))
        button.setStyleSheet("""
            QPushButton {
                background-color: #0d214f;
                color: white;
                border: none;
                border-radius: 30px;
                padding: 30px;
                min-width: 250px;
                min-height: 100px;
            }
            QPushButton:hover {
                background-color: #1a3a7a;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self.on_select_algorithm(algo_key))
        return button
