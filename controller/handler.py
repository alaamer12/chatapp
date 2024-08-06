from typing import Optional
import pickle
from PyQt5.QtCore import pyqtSlot
from datetime import datetime


class Handler:

    def __init__(self, controller):
        self.controller = controller
        self.current_user: Optional[str] = self._get_user()
        self.current_room: Optional[int] = None
        print(f"Current user: {self.current_user}")

    def signin_clicked(self, username: str, password: str):
        if self._null_check(username, password):
            return False
        success = self.controller.model.has_record(table='Users', UserID=username, Password=password)
        if success:
            self._save_user(username)
            self.current_user = username
        return success

    @staticmethod
    def _get_user():
        try:
            with open('user.pkl', 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return None

    @staticmethod
    def _save_user(user):
        with open('user.pkl', 'wb') as f:
            pickle.dump(user, f)

    def signup_clicked(self):
        registration = self.controller.view.Pages.REGISTRATION
        self.controller.view.set_page(registration)

    @staticmethod
    def _null_check(*values):
        return any([value == "" for value in values])

    def registration(self, name, username, password):
        if self._null_check(name, username, password):
            return False

        success = self.controller.model.set_newuser(name, username, password)
        if success:
            self._save_user(username)
            self.current_user = username
        return success

    @pyqtSlot(str)
    def tabs_clicked(self, label):
        if label == "Chatting":
            self.controller.view.set_page(self.controller.view.Pages.CHATTING)
        elif label == "Requests":
            self.controller.view.set_page(self.controller.view.Pages.REQUESTS)
        elif label == "Settings":
            self.controller.view.set_page(self.controller.view.Pages.SETTINGS)
        elif label == "Exit":
            self.controller.view.set_page(self.controller.view.Pages.LOGIN)

    def sending_request(self, search_value):
        return self.controller.model.send_request(self.current_user, search_value)

    def sending_message(self, message_id, message):
        now = datetime.now()
        now.strftime("%Y-%m-%d %H:%M:%S")
        return self.controller.model.send_message(self.current_user, message_id, message, now, self.current_room)

    def request_action(self, request_id, action, friend_id):
        if action == "accept":
            self.controller.model.accept_action(request_id, self.current_user, friend_id)
        elif action == "decline":
            self.controller.model.decline_action(request_id, self.current_user, friend_id)

    def requests(self):
        return self.controller.model.get_request(self.current_user)

    def rooms(self):
        results = self.controller.model.get_rooms(self.current_user)
        results_dict = {}
        for result in results:
            results_dict = {
                'RoomID': result[0],
                'FriendID': result[1],
                'UserName': result[2]
            }
        return [results_dict]

    def loading_messages(self, room_id):
        self.current_room = room_id
        print(f"Current room: {self.current_room}")
        results: list[tuple] = self.controller.model.get_messages(room_id)
        messages_list = []
        for result in results:
            results_dict = {
                'UserID': result[1],
                'Content': result[2],
                'DateTime': result[3],
                'SenderID': self.current_user
            }
            messages_list.append(results_dict)
        return messages_list
