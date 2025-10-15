import requests
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class EncryptionWindow(QWidget):
    def __init__(self, user, algorithm, on_navigate):
        super().__init__()
        self.user = user
        self.algorithm = algorithm
        self.on_navigate = on_navigate
        self.api_url = "http://localhost:5000/api"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Cryptography Toolkit - {self.algorithm.capitalize()}")
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
        back_button.clicked.connect(lambda: self.on_navigate("algorithms"))

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

        title = QLabel(self.algorithm.capitalize())
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("color: #0d214f; background-color: #e6f0ff; padding: 20px; border-radius: 15px;")
        title.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(title)
        content_layout.addSpacing(30)

        message_section = QVBoxLayout()
        message_label = QLabel("message chiffré")
        message_label.setFont(QFont("Arial", 14))
        message_label.setStyleSheet("color: #333;")

        self.encrypted_display = QTextEdit()
        self.encrypted_display.setReadOnly(True)
        self.encrypted_display.setPlaceholderText("Le message chiffré apparaîtra ici...")
        self.encrypted_display.setFont(QFont("Arial", 12))
        self.encrypted_display.setStyleSheet("""
            QTextEdit {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                padding: 15px;
                background-color: white;
            }
        """)
        self.encrypted_display.setFixedHeight(100)

        message_section.addWidget(message_label)
        message_section.addWidget(self.encrypted_display)

        content_layout.addLayout(message_section)
        content_layout.addSpacing(30)

        transmission_layout = QHBoxLayout()
        transmission_layout.setSpacing(50)

        sender_section = QVBoxLayout()
        sender_section.setAlignment(Qt.AlignCenter)

        sender_label = QLabel("💻")
        sender_label.setFont(QFont("Arial", 48))
        sender_label.setAlignment(Qt.AlignCenter)

        your_message_label = QLabel("votre message")
        your_message_label.setFont(QFont("Arial", 12))
        your_message_label.setStyleSheet("color: #666;")
        your_message_label.setAlignment(Qt.AlignCenter)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Entrez votre message...")
        self.message_input.setFont(QFont("Arial", 12))
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                padding: 15px;
                background-color: white;
            }
        """)
        self.message_input.setFixedHeight(80)

        sender_section.addWidget(sender_label)
        sender_section.addWidget(your_message_label)
        sender_section.addWidget(self.message_input)

        receiver_section = QVBoxLayout()
        receiver_section.setAlignment(Qt.AlignCenter)

        receiver_label = QLabel("💻")
        receiver_label.setFont(QFont("Arial", 48))
        receiver_label.setAlignment(Qt.AlignCenter)

        received_label = QLabel("message reçu")
        received_label.setFont(QFont("Arial", 12))
        received_label.setStyleSheet("color: #666;")
        received_label.setAlignment(Qt.AlignCenter)

        self.decrypted_display = QTextEdit()
        self.decrypted_display.setReadOnly(True)
        self.decrypted_display.setPlaceholderText("Le message déchiffré apparaîtra ici...")
        self.decrypted_display.setFont(QFont("Arial", 12))
        self.decrypted_display.setStyleSheet("""
            QTextEdit {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                padding: 15px;
                background-color: white;
            }
        """)
        self.decrypted_display.setFixedHeight(80)

        receiver_section.addWidget(receiver_label)
        receiver_section.addWidget(received_label)
        receiver_section.addWidget(self.decrypted_display)

        transmission_layout.addLayout(sender_section)

        line_widget = QLabel("━━━━━━━━━━━━━━━━━→")
        line_widget.setFont(QFont("Arial", 20))
        line_widget.setStyleSheet("color: #0d214f;")
        line_widget.setAlignment(Qt.AlignCenter)
        transmission_layout.addWidget(line_widget)

        transmission_layout.addLayout(receiver_section)

        content_layout.addLayout(transmission_layout)
        content_layout.addSpacing(30)

        bottom_section = QHBoxLayout()

        self.receiver_combo = QComboBox()
        self.receiver_combo.setFont(QFont("Arial", 12))
        self.receiver_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.receiver_combo.setFixedWidth(300)
        self.load_users()

        send_button = QPushButton("Envoyer")
        send_button.setFont(QFont("Arial", 14, QFont.Bold))
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #0d214f;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #1a3a7a;
            }
        """)
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.clicked.connect(self.handle_send)

        bottom_section.addWidget(QLabel("Destinataire:"))
        bottom_section.addWidget(self.receiver_combo)
        bottom_section.addStretch()
        bottom_section.addWidget(send_button)

        content_layout.addLayout(bottom_section)

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

    def load_users(self):
        try:
            response = requests.get(f"{self.api_url}/users/{self.user['id']}/others")
            data = response.json()

            if data.get('success'):
                users = data.get('users', [])
                for user in users:
                    self.receiver_combo.addItem(user['email'], user['id'])
            else:
                QMessageBox.warning(self, "Error", "Could not load users")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")

    def handle_send(self):
        message = self.message_input.toPlainText().strip()
        receiver_id = self.receiver_combo.currentData()

        if not message:
            QMessageBox.warning(self, "Error", "Please enter a message")
            return

        if receiver_id is None:
            QMessageBox.warning(self, "Error", "Please select a recipient")
            return

        try:
            response = requests.post(f"{self.api_url}/messages/send",
                                    json={
                                        "sender_id": self.user['id'],
                                        "receiver_id": receiver_id,
                                        "content": message,
                                        "algo_name": self.algorithm
                                    })
            data = response.json()

            if data.get('success'):
                message_data = data.get('data')
                self.encrypted_display.setPlainText(message_data['encrypted'])
                self.decrypted_display.setPlainText(message_data['content'])
                QMessageBox.information(self, "Success", "Message sent successfully!")
                self.message_input.clear()
            else:
                QMessageBox.warning(self, "Error", data.get('message'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
