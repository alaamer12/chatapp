from abc import ABC, abstractmethod


class BasePage(ABC):
    def __init__(self, controller, ui):
        self.controller = controller
        self.ui = ui

    @abstractmethod
    def initialize_page(self):
        pass

    @abstractmethod
    def _connect_signals(self):
        pass
