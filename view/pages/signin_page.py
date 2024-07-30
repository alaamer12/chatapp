from .base_page import BasePage

class SignIn(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)

    def initialize_page(self):
        print("Initializing SignIn Page")
        self.ui.invalid_signin_label.hide()
        self._connect_signals()

    def _connect_signals(self):
        print("Connecting signals in SignIn Page")
        self.ui.login_button.clicked.connect(self.on_signin_clicked)
        self.ui.signup_button.clicked.connect(self.on_signup_clicked)

    def on_signin_clicked(self):
        print("SignIn button clicked")
        username = self.ui.username_textinput.text().strip()
        password = self.ui.password_textinput.text().strip()
        self.controller.handle_signin_clicked(username, password)

    def on_signup_clicked(self):
        print("SignUp button clicked")
        self.controller.handle_signup_clicked()
