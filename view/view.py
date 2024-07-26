import sys
from PyQt5.QtWidgets import QMainWindow
from view.ui_main import Ui_MainWindow


class View(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("background-color: #333; color: white;")
        self.setWindowTitle("Chat App")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def main(self, app):
        self.show()
        sys.exit(app.exec_())
