from .db import DB
from .server import Server
from .client import Client
from .helpers.constants import HOST, PORT


class Model:
    def __init__(self):
        self.sever = Server(host=HOST, port=PORT)
        self.client = Client(host=HOST, port=PORT)
        self.db = DB()
        self.username = ""

    def set_username(self, username):
        self.username = username

    def send_message(self, message):
        pass

    def receive_message(self, message):
        pass

    def start_client(self, host, port):
        pass

    def set_room_id(self):
        pass
