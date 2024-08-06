from abc import ABC, abstractmethod
from PyQt5.QtCore import QObject
from PyQt5 import QtCore

class BasePage(QObject):
    def __init__(self, controller, ui):
        super().__init__()
        self.controller = controller
        self.ui = ui

    @staticmethod
    def _translate(context, source_text):
        return QtCore.QCoreApplication.translate(context, source_text)

    @abstractmethod
    def initialize_page(self):
        pass

    @abstractmethod
    def _connect_signals(self):
        pass
