from model.model import Model
from view.view import View
from typing import Optional
from PyQt5.QtCore import pyqtSlot


class Controller:

    def __init__(self):
        self.view: Optional[View] = None
        self.model = Model()

    def handle_signin_clicked(self, username: str, password: str):
        success = self.model.check_login(username, password)
        if success:
            self.view.set_page(self.view.Pages.CHATTING)
        else:
            self.view.show_invalid_message("invalid_signin_label")

    def handle_signup_clicked(self):
        registration = self.view.Pages.REGISTRATION
        self.view.set_page(registration)

    def handle_registration(self, name, username, password):
        success = self.model.set_newuser(name, username, password)
        if success:
            self.view.set_page(self.view.Pages.CHATTING)
        else:
            self.view.show_invalid_message("invalid_username_label")

    @pyqtSlot(str)
    def handle_tabs_clicked(self, label):
        if label == "Chatting":
            self.view.set_page(self.view.Pages.CHATTING)
        elif label == "Requests":
            self.view.set_page(self.view.Pages.REQUESTS)
        elif label == "Settings":
            self.view.set_page(self.view.Pages.SETTINGS)
        elif label == "Exit":
            self.view.close()

    def close(self):
        pass

    def main(self, _app):
        self.view = View(self)
        self.view.main(_app)
