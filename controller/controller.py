from __future__ import annotations
from model.model import Model
from view.view import View
from typing import Optional
from .handler import Handler
import pickle
import threading


class Controller:

    def __init__(self, is_running):
        self.view: Optional[View] = None
        self.model = Model()
        self._current_user = self._get_user()
        self.model.set_username(self._current_user)
        self.handle_ = Handler(self, self._current_user)
        self.start() if is_running else None
        self.model.set_message_callback(self.handle_message)

    @staticmethod
    def handle_message(message):
        print("Called")
        print(message)

    @staticmethod
    def run_once():
        """Decorator to run the function only once."""

        def wrapper(func):
            func.has_run = False

            def inner(*args, **kwargs):
                if not func.has_run:
                    result = func(*args, **kwargs)
                    func.has_run = True
                    return result
                return None  # Or raise an exception, or handle it in another way if needed.

            return inner

        return wrapper

    @run_once()
    def start(self):
        threading.Thread(target=self.model.start_server).start()
        threading.Thread(target=self.model.start_client).start()

        # Set callback to handle client list updates
        if self.model.client:
            self.model.client.set_update_clients_callback(self.handle_client_list_update)
        else:
            print("Client is not initialized properly.")

    @staticmethod
    def handle_client_list_update(clients):
        print("Updated Clients List:", clients)

    def send_message(self, message):
        self.model.send_message(message)

    @staticmethod
    def _get_user():
        try:
            with open('model/user.pkl', 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return None

    @staticmethod
    def save_user(user):
        with open('model/user.pkl', 'wb') as f:
            pickle.dump(user, f)

    def close(self):
        self.model.stop_client()
        self.model.stop_server()

    def main(self, _app):
        self.view = View(self)
        self.view.main(_app)
