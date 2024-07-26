import socket
import threading


class Client:
    def __init__(self, *, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        self.gui_done = False
        self.running = True

        self.gui_thread = threading.Thread(target=self.gui_loop)
        self.gui_thread.start()

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def gui_loop(self):
        pass

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'USERNAME':
                    self.client.send(self.username.encode('utf-8'))
                else:
                    if self.gui_done:
                        pass
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.client.close()
                break

    def send(self, message):
        try:
            self.client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.client.close()

    def stop(self):
        self.running = False
        self.client.close()
        # self.win.destroy()


if __name__ == "__main__":
    from helpers.constants import HOST, PORT
    client = Client(host=HOST, port=PORT)

