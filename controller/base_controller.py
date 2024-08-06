from model.model import Model
from view.view import View
from typing import Optional
from abc import ABC, abstractmethod


class BaseController(ABC):

    def __init__(self):
        self.view: Optional[View] = None
        self.model = Model()
