import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QSize

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Screen")
        self.setGeometry(100, 100, 800, 500)
        #self.setFixedSize(800, 500)

        # --- Main Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Left Side (Form) ---
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

        # Welcome Label
        welcome_label = QLabel("Bienvenue !")
        welcome_label.setFont(QFont("Arial", 28, QFont.Bold))
        welcome_label.setStyleSheet("color: #0d214f;")
        welcome_label.setAlignment(Qt.AlignLeft)

        # Email Input
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

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setStyleSheet(self.email_input.styleSheet()) # Reuse style

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Sign Up Button
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

        # Sign In Button
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

        button_layout.addWidget(signup_button)
        button_layout.addWidget(signin_button)
        button_layout.addStretch()


        left_layout.addWidget(welcome_label)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.email_input)
        left_layout.addWidget(self.password_input)
        left_layout.addSpacing(10)
        left_layout.addLayout(button_layout)
        left_layout.addStretch() # Pushes everything up

        # --- Right Side (Image) ---
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
        # Since we cannot directly use external images from a path in this environment,
        # we will use a placeholder or a Qt built-in icon as a replacement.
        # For a local run, you would use: pixmap = QPixmap('path/to/your/image.png')
        # Here, we use a built-in icon for demonstration.
        try:
            # We can't load the user's specific image, so we'll simulate the graphic area.
            # A good way to do this is with a colored widget or a placeholder pixmap.
            placeholder_pixmap = QPixmap(300, 300)
            placeholder_pixmap.fill(QColor("#e6f0ff"))
            image_label.setPixmap(placeholder_pixmap)
            image_label.setText("Image Placeholder")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("color: #555; font-size: 16px;")
        except Exception as e:
            print(f"Could not load image: {e}")
            image_label.setText("Image Area")


        right_layout.addWidget(image_label)

        # --- Add widgets to main layout ---
        main_layout.addWidget(left_widget, 1) # 1 stretch factor
        main_layout.addWidget(right_widget, 1) # 1 stretch factor


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.showMaximized()
    sys.exit(app.exec_())
