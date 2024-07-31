
from .base_page import BasePage


class Requests(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)

    def initialize_page(self):
        self._connect_signals()


    def _connect_tabs_signals(self):
        self.ui.requests_chatting_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_chatting_button.text().strip()))
        self.ui.requests_exit_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_exit_button.text().strip()))
        self.ui.requests_requests_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_requests_button.text().strip()))
        self.ui.requests_settings_button.clicked.connect(lambda: self.controller.handle_tabs_clicked(self.ui.chatting_settings_button.text().strip()))

    def _connect_signals(self):
        self._connect_tabs_signals()
        self.ui.request_accept_button.clicked.connect(self._on_accept_clicked)
        self.ui.request_decline_button.clicked.connect(self._on_decline_clicked)
        self.ui.send_button.clicked.connect(self._on_send_clicked)

    def _on_send_clicked(self):
        pass

    async def _load_requests(self):
        pass

    def _on_accept_clicked(self):
        pass

    def _on_decline_clicked(self):
        pass

