from .db import DB
from .server import Server
from .client import Client
from .helpers.constants import HOST, PORT, DB_LOCALHOST, DB_NAME, DB_USER, DB_PASSWORD


class Model:
    def __init__(self):
        self.sever = Server(host=HOST, port=PORT)
        self.client = Client(host=HOST, port=PORT)
        self.db = DB(localhost=DB_LOCALHOST, user=DB_USER,
                     password=DB_PASSWORD, database=DB_NAME)
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
