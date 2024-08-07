from typing import Optional
import threading
from PyQt5.QtCore import pyqtSlot
from datetime import datetime


class Handler:
    room_id_clicked = None

    def __init__(self, controller, current_user):
        self.controller = controller
        self.current_user: Optional[str] = current_user
        self.current_room: Optional[int] = None
        print(f"Current user: {self.current_user}")

    def signin_clicked(self, username: str, password: str):
        if self._null_check(username, password):
            return False
        success = self.controller.model.has_record(table='Users', UserID=username, Password=password)
        if success:
            self.controller.save_user(username)
            self.current_user = username
        return success

    def signup_clicked(self):
        registration = self.controller.view.Pages.REGISTRATION
        self.controller.view.set_page(registration)

    @staticmethod
    def _null_check(*values):
        return any([value == "" for value in values])

    def registration(self, name, username, password):
        if self._null_check(name, username, password):
            return False

        success = self.controller.model.set_new_user(name, username, password)
        if success:
            self.controller.save_user(username)
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

    def sending_message(self, message):
        now = datetime.now()
        now.strftime("%Y-%m-%d %H:%M:%S")
        result = self.controller.model.save_message(self.current_user, message, now, self.current_room)
        if result:
            self.controller.send_message(message)
            return result

    def request_action(self, request_id, action, friend_id):
        if action == "accept":
            self.controller.model.save_accept_action(request_id, self.current_user, friend_id)
        elif action == "decline":
            self.controller.model.save_decline_action(request_id, self.current_user, friend_id)

    def requests(self):
        return self.controller.model.fetch_requests(self.current_user)

    def rooms(self):
        results = self.controller.model.fetch_rooms(self.current_user)
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
        self.start_client_thread()
        results: list[tuple] = self.controller.model.fetch_messages(room_id)
        messages_list = []
        for result in results:
            results_dict = {
                'MessageID': result[0],
                'UserID': result[1],
                'Content': result[2],
                'DateTime': result[3],
                'SenderID': self.current_user
            }
            messages_list.append(results_dict)
        return messages_list

    def start_client_thread(self):
        print("Clicked Room:", self.current_room)
        client_thread = threading.Thread(target=self.controller.model.start_client)
        client_thread.start()

