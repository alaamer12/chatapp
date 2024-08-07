import socket
import threading
from .helpers.printer import print_info, print_error


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
            self.__clients: dict = {}
            self.__usernames: dict = {}
            self.__current_users = []
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__server.bind((host, port))
            self.__server.listen()

            self._initialized = True

    @property
    def clients(self):
        return self.__current_users

    def broadcast(self, message):
        print_info(f"Broadcasting message: {message.decode('utf-8')}")  # Debug statement
        for client in list(self.__clients.keys()):
            try:
                client.send(message)
            except Exception as e:
                self._remove_client(client)
                print_error(f"Error: {e}")

    def start(self):
        while True:
            try:
                client, address = self.__server.accept()
                print_info(f"Connected with {str(address)}")

                client.send('USERNAME: '.encode('utf-8'))
                username = client.recv(1024).decode('utf-8')

                self.__clients[client] = username
                self.__usernames[client] = username

                self.__current_users.append(username)
                print_info(f"Nickname of the client is {username}")

                self.broadcast(f"{username} joined the chat!".encode('utf-8'))
                print()
                client.send('Connected to the server!'.encode('utf-8'))

                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except Exception as e:
                print_error(f"Error: {e}")

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    self.broadcast(message)
                    self.send_client_list_update()  # Update clients list after message
                else:
                    raise Exception("Client disconnected")
            except Exception as e:
                self._remove_client(client)
                print_error(f"Error: {e}")
                break

    def send_client_list_update(self):
        clients_list = ','.join(self.__usernames.values())
        self.broadcast(f"UPDATE_CLIENTS:{clients_list}".encode('utf-8'))

    def _remove_client(self, client):
        client.close()
        del self.__clients[client]
        username = self.__usernames.pop(client, None)
        if username:
            self.broadcast(f'{username} left the chat!'.encode('utf-8'))

    def close(self):
        for client in list(self.__clients.keys()):
            self._remove_client(client)
        self.__server.close()


def start_server():
    print("Starting Server...")
    from .helpers.constants import HOST, PORT

    server = Server(host=HOST, port=PORT)
    print("Server is running...")
    try:
        while True:
            try:
                server.start()  # Run the server's main loop
            except Exception as e:
                print_error(f"Error in server loop: {e}")
            finally:
                server.close()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    except Exception as e:
        print_error(f"Error: {e}")
    finally:
        server.close()



if __name__ == "__main__":
    start_server()
