from .base_page import BasePage


class SignUp(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)
        self.initialize_page()

    def initialize_page(self):
        self.ui.invalid_username_label.hide()
        self._connect_signals()

    def _connect_signals(self):
        self.ui.registration_button.clicked.connect(self.on_registration)

    def on_registration(self):
        name = self.ui.name_textinput.text().strip()
        username = self.ui.username_textinput_2.text().strip()
        password = self.ui.password_textinput_2.text().strip()
        success = self.controller.handle_.registration(name, username, password)
        if success:
            self.controller.view.set_page(self.controller.view.Pages.CHATTING)
            self.ui.invalid_username_label.hide()
        else:
            self.ui.invalid_username_label.show()

