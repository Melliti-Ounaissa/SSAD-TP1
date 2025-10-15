import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from ui.auth_window import AuthWindow
from ui.home_window import HomeWindow
from ui.algorithms_window import AlgorithmsWindow
from ui.encryption_window import EncryptionWindow
from ui.messages_window import MessagesWindow


class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stacked_widget = QStackedWidget()
        self.current_user = None

        self.auth_window = AuthWindow(self.on_auth_success)
        self.stacked_widget.addWidget(self.auth_window)
        self.stacked_widget.setCurrentWidget(self.auth_window)

        self.stacked_widget.setWindowTitle("Cryptography Toolkit")
        self.stacked_widget.showMaximized()

    def on_auth_success(self, user):
        self.current_user = user
        self.show_home()

    def show_home(self):
        home_window = HomeWindow(self.current_user, self.navigate)
        self.stacked_widget.addWidget(home_window)
        self.stacked_widget.setCurrentWidget(home_window)

    def navigate(self, page):
        if page == "home":
            self.show_home()
        elif page == "algorithms":
            self.show_algorithms()
        elif page == "messages":
            self.show_messages()
        elif page == "attacks":
            print("Attacks page not implemented yet")

    def show_algorithms(self):
        algorithms_window = AlgorithmsWindow(
            self.current_user,
            self.navigate,
            self.show_encryption
        )
        self.stacked_widget.addWidget(algorithms_window)
        self.stacked_widget.setCurrentWidget(algorithms_window)

    def show_encryption(self, algorithm):
        encryption_window = EncryptionWindow(
            self.current_user,
            algorithm,
            self.navigate
        )
        self.stacked_widget.addWidget(encryption_window)
        self.stacked_widget.setCurrentWidget(encryption_window)

    def show_messages(self):
        messages_window = MessagesWindow(self.current_user, self.navigate)
        self.stacked_widget.addWidget(messages_window)
        self.stacked_widget.setCurrentWidget(messages_window)

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = MainApplication()
    app.run()
