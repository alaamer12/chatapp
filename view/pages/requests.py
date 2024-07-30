from .base_page import BasePage


class Requests(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)

    def initialize_page(self):
        pass

    async def load_page(self):
        pass

    def _connect_signals(self):
        pass
