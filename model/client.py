import socket
import threading
from typing import Optional
import pickle


class Client:
    def __init__(self, *, host, port):
        self.receive_thread: Optional[threading.Thread] = None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = self.load_user()
        self.running = True
        self.message_callback = None
        self.clients = []

    def set_username(self, username):
        self.username = username if username else self.load_user()

    @staticmethod
    def load_user():
        try:
            with open('model/user.pkl', 'rb') as f:
                username = pickle.load(f)
                return username
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print("Error loading user")
            pass

    def set_message_callback(self, callback):
        self.message_callback = callback

    def send(self, message):
        try:
            self.client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.stop()

    def start(self):
        print("Starting Client...")
        print(f"Connected with {self.client.getpeername()}")
        self.client.send(self.username.encode('utf-8'))
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if self.message_callback:
                    self.message_callback(message)
                if message.startswith("UPDATE_CLIENTS:"):
                    print(message)
                    self.update_clients_list(message[len("UPDATE_CLIENTS:"):])
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.stop()

    def update_clients_list(self, client):
        self.clients.append(client)


    def stop(self):
        self.running = False
        self.client.close()
