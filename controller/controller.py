from __future__ import annotations
from model.model import Model
from view.view import View
from typing import Optional
from .handler import Handler
from .getter import Getter


class Controller:

    def __init__(self):
        self.view: Optional[View] = None
        self.model = Model()
        self.handle_ = Handler(self)
        self.get_ = Getter(self)

    def close(self):
        pass

    def main(self, _app):
        self.view = View(self)
        self.view.main(_app)



