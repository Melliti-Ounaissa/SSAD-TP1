import sys
import requests
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt


class AuthWindow(QWidget):
    def __init__(self, on_auth_success):
        super().__init__()
        self.on_auth_success = on_auth_success
        self.api_url = "http://localhost:5000/api"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cryptography Toolkit - Authentication")
        self.setGeometry(100, 100, 800, 500)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_widget = QWidget()
        left_widget.setObjectName("leftWidget")
        left_widget.setStyleSheet("""
            #leftWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                 stop:0 rgba(240, 245, 255, 255),
                                                 stop:1 rgba(255, 255, 255, 255));
            }
        """)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(50, 50, 50, 50)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(20)

        welcome_label = QLabel("Bienvenue !")
        welcome_label.setFont(QFont("Arial", 28, QFont.Bold))
        welcome_label.setStyleSheet("color: #0d214f;")
        welcome_label.setAlignment(Qt.AlignLeft)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFont(QFont("Arial", 12))
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 20px;
                padding: 10px 20px;
                background-color: white;
                height: 25px;
            }
            QLineEdit:focus {
                border: 1px solid #4a90e2;
            }
        """)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setStyleSheet(self.email_input.styleSheet())

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        signup_button = QPushButton("Sign Up")
        signup_button.setFont(QFont("Arial", 12, QFont.Bold))
        signup_button.setCursor(Qt.PointingHandCursor)
        signup_button.setStyleSheet("""
            QPushButton {
                background-color: #0d214f;
                color: white;
                border-radius: 20px;
                padding: 12px 25px;
                margin-right: 25px;
            }
            QPushButton:hover {
                background-color: #1a3a7a;
            }
        """)
        signup_button.clicked.connect(self.handle_signup)

        signin_button = QPushButton("Sign In")
        signin_button.setFont(QFont("Arial", 12, QFont.Bold))
        signin_button.setCursor(Qt.PointingHandCursor)
        signin_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 20px;
                padding: 12px 25px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        signin_button.clicked.connect(self.handle_signin)

        button_layout.addWidget(signup_button)
        button_layout.addWidget(signin_button)
        button_layout.addStretch()

        left_layout.addWidget(welcome_label)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.email_input)
        left_layout.addWidget(self.password_input)
        left_layout.addSpacing(10)
        left_layout.addLayout(button_layout)
        left_layout.addStretch()

        right_widget = QWidget()
        right_widget.setObjectName("rightWidget")
        right_widget.setStyleSheet("""
            #rightWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                 stop:0 rgba(240, 245, 255, 255),
                                                 stop:1 rgba(220, 230, 255, 255));
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setAlignment(Qt.AlignCenter)

        image_label = QLabel()
        placeholder_pixmap = QPixmap(300, 300)
        placeholder_pixmap.fill(QColor("#e6f0ff"))
        image_label.setPixmap(placeholder_pixmap)
        image_label.setText("Security Image")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("color: #555; font-size: 16px;")

        right_layout.addWidget(image_label)

        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

    def handle_signup(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return

        try:
            response = requests.post(f"{self.api_url}/auth/signup",
                                    json={"email": email, "password": password})
            data = response.json()

            if data.get('success'):
                QMessageBox.information(self, "Success", data.get('message'))
                user = data.get('user')
                self.on_auth_success(user)
            else:
                QMessageBox.warning(self, "Error", data.get('message'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")

    def handle_signin(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return

        try:
            response = requests.post(f"{self.api_url}/auth/signin",
                                    json={"email": email, "password": password})
            data = response.json()

            if data.get('success'):
                user = data.get('user')
                self.on_auth_success(user)
            else:
                QMessageBox.warning(self, "Error", data.get('message'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
