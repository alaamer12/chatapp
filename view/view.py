import sys
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5.QtCore import Qt, QEvent
from view.ui_main import Ui_MainWindow


class View(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Chat App")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.messages_scrollarea.hide()

        # Assuming room is a QLabel or another QWidget
        self.ui.room.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress and source == self.ui.room:
            self.ui.messages_scrollarea.show()
            return True
        return super().eventFilter(source, event)

    def main(self, app):
        self.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = View(None)
    window.main(app)
