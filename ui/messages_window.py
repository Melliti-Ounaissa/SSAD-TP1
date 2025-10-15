import requests
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer


class MessagesWindow(QWidget):
    def __init__(self, user, on_navigate):
        super().__init__()
        self.user = user
        self.on_navigate = on_navigate
        self.api_url = "http://localhost:5000/api"
        self.init_ui()
        self.load_messages()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_messages)
        self.refresh_timer.start(3000)

    def init_ui(self):
        self.setWindowTitle("Cryptography Toolkit - Messages")
        self.setGeometry(100, 100, 1200, 700)

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
        content_layout.setContentsMargins(50, 40, 50, 40)

        title = QLabel("Messages")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("color: #0d214f;")
        title.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(title)
        content_layout.addSpacing(20)

        messages_layout = QHBoxLayout()
        messages_layout.setSpacing(30)

        sent_section = QVBoxLayout()
        sent_label = QLabel("Messages Envoyés")
        sent_label.setFont(QFont("Arial", 18, QFont.Bold))
        sent_label.setStyleSheet("color: #0d214f;")

        self.sent_scroll = QScrollArea()
        self.sent_scroll.setWidgetResizable(True)
        self.sent_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                background-color: white;
            }
        """)

        self.sent_container = QWidget()
        self.sent_layout = QVBoxLayout(self.sent_container)
        self.sent_layout.setAlignment(Qt.AlignTop)
        self.sent_layout.setSpacing(10)
        self.sent_scroll.setWidget(self.sent_container)

        sent_section.addWidget(sent_label)
        sent_section.addWidget(self.sent_scroll)

        received_section = QVBoxLayout()
        received_label = QLabel("Messages Reçus")
        received_label.setFont(QFont("Arial", 18, QFont.Bold))
        received_label.setStyleSheet("color: #0d214f;")

        self.received_scroll = QScrollArea()
        self.received_scroll.setWidgetResizable(True)
        self.received_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                background-color: white;
            }
        """)

        self.received_container = QWidget()
        self.received_layout = QVBoxLayout(self.received_container)
        self.received_layout.setAlignment(Qt.AlignTop)
        self.received_layout.setSpacing(10)
        self.received_scroll.setWidget(self.received_container)

        received_section.addWidget(received_label)
        received_section.addWidget(self.received_scroll)

        messages_layout.addLayout(sent_section)
        messages_layout.addLayout(received_section)

        content_layout.addLayout(messages_layout)

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

    def load_messages(self):
        try:
            sent_response = requests.get(f"{self.api_url}/messages/sent/{self.user['id']}")
            received_response = requests.get(f"{self.api_url}/messages/received/{self.user['id']}")

            sent_data = sent_response.json()
            received_data = received_response.json()

            self.clear_layout(self.sent_layout)
            self.clear_layout(self.received_layout)

            if sent_data.get('success'):
                for message in sent_data.get('messages', []):
                    self.add_message_card(self.sent_layout, message, is_sent=True)

            if received_data.get('success'):
                for message in received_data.get('messages', []):
                    self.add_message_card(self.received_layout, message, is_sent=False)

        except Exception as e:
            print(f"Error loading messages: {str(e)}")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_message_card(self, layout, message, is_sent):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout(card)

        if is_sent:
            recipient_email = message.get('users', {}).get('email', 'Unknown')
            header = QLabel(f"À: {recipient_email}")
        else:
            sender_email = message.get('users', {}).get('email', 'Unknown')
            header = QLabel(f"De: {sender_email}")

        header.setFont(QFont("Arial", 11, QFont.Bold))
        header.setStyleSheet("color: #0d214f;")

        algo_label = QLabel(f"Algorithme: {message.get('algo_name', 'N/A').capitalize()}")
        algo_label.setFont(QFont("Arial", 10))
        algo_label.setStyleSheet("color: #666;")

        date_label = QLabel(f"Date: {message.get('date_created', '')[:19]}")
        date_label.setFont(QFont("Arial", 9))
        date_label.setStyleSheet("color: #999;")

        if is_sent:
            content_label = QLabel(f"Message: {message.get('content', '')}")
        else:
            content_label = QLabel(f"Message: {message.get('content', '')}")

        content_label.setFont(QFont("Arial", 10))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #333; margin-top: 5px;")

        encrypted_label = QLabel(f"Chiffré: {message.get('encrypted', '')}")
        encrypted_label.setFont(QFont("Arial", 9))
        encrypted_label.setWordWrap(True)
        encrypted_label.setStyleSheet("color: #888; margin-top: 3px;")

        card_layout.addWidget(header)
        card_layout.addWidget(algo_label)
        card_layout.addWidget(date_label)
        card_layout.addWidget(content_label)
        card_layout.addWidget(encrypted_label)

        layout.addWidget(card)
