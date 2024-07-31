from .base_page import BasePage

class Settings(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)

    def initialize_page(self):
        self._connect_signals()

    def _connect_tabs_signals(self):
        self.ui.settings_chatting_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_chatting_button.text().strip()))
        self.ui.settings_exit_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_exit_button.text().strip()))
        self.ui.settings_requests_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_requests_button.text().strip()))
        self.ui.settings_settings_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_settings_button.text().strip()))

    def _connect_signals(self):
        self._connect_tabs_signals()
