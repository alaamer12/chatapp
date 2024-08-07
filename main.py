from controller.controller import Controller
import sys
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    is_running = True
    controller = Controller(is_running)
    app = QApplication(sys.argv)
    controller.main(app)
