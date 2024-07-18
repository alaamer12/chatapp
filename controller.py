from model import Model
from view import View
from typing import Optional


class Controller:

    def __init__(self):
        self.view: Optional[View] = None
        self.model = Model()

    def main(self, app):
        # ! You must initialize view with none at __init__ and use it at main function
        # ! It leads to leak in memory which leads to crashing
        self.view = View(self)
        self.view.main(app)
