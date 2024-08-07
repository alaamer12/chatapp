from .db import DB
from .helpers.constants import HOST, PORT, DB_LOCALHOST, DB_NAME, DB_USER, DB_PASSWORD
from datetime import datetime
import threading


class Model:
    def __init__(self):
        self.client = None
        self.server = None
        self.message_callback = None
        self.db = DB(localhost=DB_LOCALHOST, user=DB_USER,
                     password=DB_PASSWORD, database=DB_NAME)
        self.username = ""

    @staticmethod
    def __generate_id():
        from uuid import uuid4
        return int(datetime.now().timestamp())

    def _generate_room_id(self):
        return self.__generate_id()

    def _generate_message_id(self):
        return self.__generate_id()

    def _generate_request_id(self):
        return self.__generate_id()

    def save_message(self, current_user, message, now, room_id):
        message_id = self._generate_message_id()
        self.db.add_to("Message", MessageID=message_id, UserID=current_user, Content=message, DateTime=now,
                       RoomID=room_id)
        return message_id

    def fetch_rooms(self, user_id):
        condition = f"UserID = '{user_id}' OR FriendID = '{user_id}'"
        return self.db.get_all_where("Friends", condition, "RoomID", "FriendID", "UserName")

    def _fetch_user_name(self, user_id):
        result = self.db.get_one("Users", "UserID", user_id)
        return result[2] if result and result[2] else "Unknown"

    def save_accept_action(self, request_id: int, user_id: str, friend_id: str):
        self.db.update_at("Users", condition=f"UserID = '{friend_id}'", IsAccept=1)
        self.db.update_at("Requests", condition=f"RequestID = {request_id}", IsAccept=1)

        friend_name = self._fetch_user_name(friend_id)
        user_name = self._fetch_user_name(user_id)
        room_id = self._generate_room_id()

        self.db.add_to("Friends", RoomID=room_id, UserID=user_id, FriendID=friend_id, UserName=user_name,
                       FriendName=friend_name)

        return room_id

    def save_decline_action(self, request_id: int, user_id: str, friend_id: str):
        self.db.delete_rows("Requests", condition=f"RequestID = {request_id}")
        self.db.delete_columns("Users", condition=f"UserID = '{friend_id}'")
        self.db.delete_columns("Users", condition=f"UserID = '{user_id}'")

    def send_request(self, current_user, search_value):
        if not self.has_record('Users', UserID=search_value):
            return False

        if self.has_record("Requests", UserID=current_user, FriendID=search_value):
            return False

        now = datetime.now()
        self.db.update_at("Users", condition=f"UserID = '{current_user}'", FriendID=search_value)
        self.db.update_at("Users", condition=f"UserID = '{search_value}'", FriendID=current_user)

        self.db.add_to('Requests', RequestID=self._generate_request_id(), UserID=current_user, FriendID=search_value,
                       IsAccept=0,
                       RequestDateTime=now.strftime("%Y-%m-%d %H:%M:%S"))
        return True

    def has_record(self, table, **kwargs):
        results = self.db.get_all(table, *kwargs.keys())
        if results:
            for record in results:
                record_dict = dict(zip(kwargs.keys(), record))
                if all(record_dict[col] == val for col, val in kwargs.items()):
                    return True
        return False

    def _check_existing(self, username):
        return self.has_record('Users', UserID=username)

    def set_new_user(self, name, username, password):
        if self._check_existing(username):
            return False
        try:
            self.db.add_to('Users', UserName=name, UserID=username, Password=password, IsOnline=1, IsAccept=0)
        except Exception as e:
            print(f"Error adding new user: {e}")
            return False
        return self._check_existing(username)

    def fetch_requests(self, current_user) -> list[dict]:
        results = self.db.get_all('Requests', 'RequestID', 'UserID', 'FriendID', 'IsAccept', 'RequestDateTime')
        name_results = self.db.get_inner_join('Requests', 'Users', 'UserID', 'UserID', 'UserName')

        if name_results is None:
            return []

        user_names = {result[0]: result[1] for result in name_results if len(result) >= 2 and result[0]}

        request_list = [
            {
                'RequestID': result[0],
                'UserID': result[1],
                'Name': user_names.get(result[1], 'Unknown'),
                'FriendID': result[2],
                'IsAccept': result[3],
                'RequestDateTime': result[4]
            }
            for result in results if len(result) >= 5 and result[2] == current_user and result[3] != 1
        ]

        return request_list

    def fetch_messages(self, room_id: int) -> list:
        condition = f"RoomID = {room_id} ORDER BY DateTime DESC"
        return self.db.get_all_where('Message', condition)

    def set_username(self, username):
        self.username = username

    def set_message_callback(self, callback):
        self.message_callback = callback
        if self.client:
            self.client.set_message_callback(callback)

    def start_server(self):
        from .server import start_server as ss
        ss()

    def start_client(self):
        from .client import Client
        self.client = Client(host=HOST, port=PORT)
        self.client.set_username(self.username)
        if self.message_callback:
            self.client.set_message_callback(self.message_callback)
        self.client.start()

    def send_message(self, message):
        if self.client:
            self.client.send(message)

    def stop_client(self):
        if self.client:
            self.client.stop()

    def stop_server(self):
        if self.server:
            self.server.join()

    def get_clients(self) -> set:
        if self.server:
            try:
                return self.server.clients
            except Exception:
                pass
