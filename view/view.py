import sys
from PyQt5.QtWidgets import QMainWindow
from view.ui_main import Ui_MainWindow
from .pages.chatting_page import Chatting
from .pages.requests_page import Requests
from .pages.settings_page import Settings
from .pages.signin_page import SignIn
from .pages.signup_page import SignUp
from .pages.constants import Pages as EnumPages


class View(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Chat App")
        self.Pages = EnumPages

        # Initialize pages
        self.pages = {
            self.Pages.LOGIN: SignIn(controller, self.ui),
            self.Pages.REGISTRATION: SignUp(controller, self.ui),
            self.Pages.CHATTING: Chatting(controller, self.ui),
            self.Pages.SETTINGS: Settings(controller, self.ui),
            self.Pages.REQUESTS: Requests(controller, self.ui),
        }

        # Set initial page
        self.set_page(self.Pages.REQUESTS)

    def set_page(self, page: EnumPages) -> None:
        try:
            page_index: int = page.value
            self.ui.pages_stack.setCurrentIndex(page_index)
            page_obj = self.pages.get(page)
            if page_obj:
                page_obj.initialize_page()
            else:
                print(f"No page object found for {page}")
        except Exception as e:
            print(f"Error setting page {page}: {e}")

    def show_invalid_message(self, label_name: str):
        label = getattr(self.ui, label_name, None)
        if label:
            label.show()
        else:
            print(f"Label {label_name} not found")

    def closeEvent(self, event):
        pass
        # self.controller.model.close()

    def main(self, _app):
        self.show()
        sys.exit(_app.exec_())
