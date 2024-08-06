import socket
from .helpers.printer import print_info, print_error
import threading


class Server:
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, *, host, port):
        if not hasattr(self, '_initialized'):
            self.__clients = {}
            self.__usernames = {}

            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set SO_REUSEADDR option to allow reuse of the address
            self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__server.bind((host, port))
            self.__server.listen()

            self._initialized = True

    def broadcast(self, message):
        for client in list(self.__clients.keys()):
            try:
                client.send(message)
            except Exception as e:
                client.close()
                del self.__clients[client]
                username = self.__usernames.pop(client, None)
                if username:
                    self.broadcast(f'{username} left the chat!'.encode('utf-8'))
                print_error(f"Error: {e}")

    def start(self):
        while True:
            client, address = self.__server.accept()
            print_info(f"Connected with {str(address)}")

            client.send('USERNAME'.encode('utf-8'))

            username = client.recv(1024).decode('utf-8')

            self.__clients[client] = username
            self.__usernames[client] = username
            print_info(f"Nickname of the client is {username}")

            self.broadcast(f"{username} joined the chat!".encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8'))

            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    print(f"{message.decode('utf-8')}")
                    self.broadcast(message)
                else:
                    raise Exception("Client disconnected")
            except Exception as e:
                client.close()
                del self.__clients[client]
                username = self.__usernames.pop(client, None)
                if username:
                    self.broadcast(f'{username} left the chat!'.encode('utf-8'))
                print_error(f"Error: {e}")
                break

    def close(self):
        self.__server.close()


if __name__ == "__main__":
    from .helpers.constants import HOST, PORT

    server = Server(host=HOST, port=PORT)
    print("Server is running...")
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    except Exception as e:
        print_error(f"Error: {e}")
    finally:
        server.close()
