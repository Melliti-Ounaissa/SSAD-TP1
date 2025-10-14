import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QIcon

class LoginWindow(QMainWindow):
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle("Login Application")
        self.setFixedSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 80, 60, 80)
        
        # Left side - Login form
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(30)
        
        # Title
        title = QLabel("Bienvenue !")
        title.setFont(QFont("Arial", 48, QFont.Bold))
        title.setStyleSheet("color: #1e3a5f;")
        left_layout.addWidget(title)
        
        left_layout.addSpacing(40)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("@ Email")
        self.email_input.setFont(QFont("Arial", 14))
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 15px 20px 15px 50px;
                border: 2px solid #d0d0e0;
                border-radius: 30px;
                background-color: white;
                color: #666;
            }
            QLineEdit:focus {
                border: 2px solid #1e3a5f;
            }
        """)
        self.email_input.setMinimumHeight(60)
        left_layout.addWidget(self.email_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒 Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 15px 20px 15px 50px;
                border: 2px solid #d0d0e0;
                border-radius: 30px;
                background-color: white;
                color: #666;
            }
            QLineEdit:focus {
                border: 2px solid #1e3a5f;
            }
        """)
        self.password_input.setMinimumHeight(60)
        left_layout.addWidget(self.password_input)
        
        left_layout.addSpacing(20)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Sign Up button
        signup_btn = QPushButton("Sign Up")
        signup_btn.setFont(QFont("Arial", 16, QFont.Bold))
        signup_btn.setMinimumSize(180, 60)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                color: white;
                border: none;
                border-radius: 30px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #2d4a6f;
            }
            QPushButton:pressed {
                background-color: #152a45;
            }
        """)
        signup_btn.clicked.connect(self.on_signup)
        buttons_layout.addWidget(signup_btn)
        
        # Sign In button
        signin_btn = QPushButton("Sign In")
        signin_btn.setFont(QFont("Arial", 16, QFont.Bold))
        signin_btn.setMinimumSize(180, 60)
        signin_btn.setCursor(Qt.PointingHandCursor)
        signin_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1e3a5f;
                border: 3px solid #1e3a5f;
                border-radius: 30px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #f0f0f5;
            }
            QPushButton:pressed {
                background-color: #e0e0ea;
            }
        """)
        signin_btn.clicked.connect(self.on_signin)
        buttons_layout.addWidget(signin_btn)
        
        left_layout.addLayout(buttons_layout)
        left_layout.addStretch()
        
        # Add left widget to main layout
        main_layout.addWidget(left_widget, 1)
        
        # Right side - Illustration placeholder
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_widget)
        
        illustration_label = QLabel("🔐")
        illustration_label.setFont(QFont("Arial", 120))
        illustration_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(illustration_label)
        
        main_layout.addWidget(right_widget, 1)
        
        # Set gradient background
        self.set_gradient_background()
    
    def set_gradient_background(self):
        """Set a gradient background for the window"""
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(200, 210, 240))
        gradient.setColorAt(1.0, QColor(230, 235, 250))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    
    def on_signup(self):
        """Handle Sign Up button click"""
        email = self.email_input.text()
        password = self.password_input.text()
        print(f"[v0] Sign Up clicked - Email: {email}")
        # Add your signup logic here
    
    def on_signin(self):
        """Handle Sign In button click"""
        email = self.email_input.text()
        password = self.password_input.text()
        print(f"[v0] Sign In clicked - Email: {email}")
        # Add your signin logic here

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
