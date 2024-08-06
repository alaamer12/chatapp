from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton
from .base_page import BasePage
from typing import Optional, Dict
from faker import Faker
from .constants import NEXT_REQUEST_PADDING, SAFE_REQUESTS_AREA_SIZE

fake = Faker()


class Requests(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)
        self.accept_button: Optional[QPushButton] = None
        self.decline_button: Optional[QPushButton] = None
        self.next_request_y = 0
        self.request_widgets: Dict[int, QtWidgets.QWidget] = {}
        requests: list[dict] = None
        # self.initialize_page()

    @staticmethod
    def run_once(fn):
        """Decorator to ensure a function is only run once."""

        def wrapper(*args, **kwargs):
            if not wrapper.has_run:
                wrapper.has_run = True
                return fn(*args, **kwargs)

        wrapper.has_run = False
        return wrapper

    # @run_once
    def initialize_page(self):
        print("Initializing Requests Page...")
        self._initialize_layout()
        self._populate_requests()
        self._connect_signals()

    def _initialize_layout(self):
        print("Initializing Layout...")
        # Ensure the scroll area has a layout set
        if not self.ui.request_scrollArea_contents.layout():
            self.ui.request_scrollArea_contents.setLayout(QtWidgets.QVBoxLayout())

    def _connect_tab_signals(self):
        self.ui.requests_chatting_button.clicked.connect(
            lambda: self.controller.handle_.tabs_clicked(self.ui.chatting_chatting_button.text().strip()))
        self.ui.requests_exit_button.clicked.connect(
            lambda: self.controller.handle_.tabs_clicked(self.ui.chatting_exit_button.text().strip()))
        self.ui.requests_requests_button.clicked.connect(
            lambda: self.controller.handle_.tabs_clicked(self.ui.chatting_requests_button.text().strip()))
        self.ui.requests_settings_button.clicked.connect(
            lambda: self.controller.handle_.tabs_clicked(self.ui.chatting_settings_button.text().strip()))

    def _connect_signals(self):
        self._connect_tab_signals()
        self.ui.send_button.clicked.connect(self._on_send_clicked)

    def _on_send_clicked(self):
        friend_username = self.ui.send_textinput.text().strip()
        if not friend_username:
            self._set_friend_request_label("Please enter a username", "red")
        success = self.controller.handle_.sending_request(friend_username)
        if success:
            self._set_friend_request_label("Request sent!", "green")
        else:
            self._set_friend_request_label("Request failed!", "red")

    def _set_friend_request_label(self, text: str, color: str):
        self.ui.friend_request_label.setText(text)
        self.ui.friend_request_label.setStyleSheet(f"color: {color}")

    def _create_request_widget(self, fullname, username, date: str, y_position: int, request_id: int):
        widget = QtWidgets.QWidget(self.ui.request_scrollArea_contents)
        widget.setGeometry(QtCore.QRect(0, y_position, 231, 161))
        widget.setObjectName(f"request_{request_id}")

        label_request = QtWidgets.QLabel("Request:", widget)
        label_request.setGeometry(QtCore.QRect(10, 10, 47, 13))
        label_request.setStyleSheet("color: white")

        name_label = QtWidgets.QLabel(fullname, widget)
        name_label.setGeometry(QtCore.QRect(10, 30, 211, 16))
        name_label.setStyleSheet("color: white")

        date_label = QtWidgets.QLabel(
            f"<html><head/><body><p>Sent a request to chat with <br/>you at: {date}</p></body></html>",
            widget
        )
        date_label.setGeometry(QtCore.QRect(10, 70, 201, 41))
        date_label.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
        date_label.setStyleSheet("color: white;")
        date_label.setWordWrap(True)

        button_container = QtWidgets.QWidget(widget)
        button_container.setGeometry(QtCore.QRect(20, 110, 181, 41))
        button_layout = QtWidgets.QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        accept_button = QPushButton("Accept", button_container)
        accept_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        accept_button.setStyleSheet("background-color: #444444; color: #E0E0E0; border-radius: 5px;"
                                    " width: 70px; height: 35px;")
        button_layout.addWidget(accept_button)

        button_layout.addItem(
            QtWidgets.QSpacerItem(8, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        decline_button = QPushButton("Decline", button_container)
        decline_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        decline_button.setStyleSheet("background-color: #CF6679; color: #E0E0E0; border-radius: 5px;"
                                     " width: 70px; height: 35px;")
        button_layout.addWidget(decline_button)

        username_label = QtWidgets.QLabel(username, widget)
        username_label.setGeometry(QtCore.QRect(10, 50, 211, 16))
        username_label.setStyleSheet("color: #A0A0A0")

        separator = QtWidgets.QFrame(widget)
        separator.setGeometry(QtCore.QRect(0, 150, 231, 20))
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.request_widgets[request_id] = widget

        accept_button.clicked.connect(lambda: self._on_request_action(request_id, "accept"))
        decline_button.clicked.connect(lambda: self._on_request_action(request_id, "decline"))

    def _populate_requests(self):
        self._clear_requests()
        self.requests: list[dict] = self.controller.handle_.requests()
        num_requests = len(self.requests)
        if num_requests > 0:
            for i in range(num_requests):
                self._create_request_widget(
                    fullname=self.requests[i]["Name"],
                    username=self.requests[i]["UserID"],
                    date=self.requests[i]["RequestDateTime"],
                    y_position=self.next_request_y,
                    request_id=self.requests[i]["RequestID"]
                )
                self.next_request_y += NEXT_REQUEST_PADDING

        if num_requests > SAFE_REQUESTS_AREA_SIZE:
            self.ui.request_scrollArea_contents.setMinimumHeight(self.next_request_y)

    def _clear_requests(self):
        print("Clearing Requests...")
        for widget in list(self.request_widgets.values()):
            widget.deleteLater()
        self.request_widgets.clear()
        self.ui.request_scrollArea_contents.setMinimumHeight(0)

    def _on_request_action(self, request_id: int, action: str):
        print(self.requests)
        userid = self.requests[request_id]["UserID"]
        print(userid)
        if self._on_request_action_helper(request_id):
            self.controller.handle_.request_action(request_id, action, userid)

    def _on_request_action_helper(self, request_id: int) -> bool:
        if request_id in self.request_widgets:
            widget = self.request_widgets.pop(request_id)
            y_position = widget.geometry().y()
            widget.deleteLater()

            if not self.request_widgets:
                self._clear_requests()
            else:
                self._update_request_positions(request_id, y_position)
            return True
        return False

    def _update_request_positions(self, removed_id: int, start_y: int):
        sorted_ids = sorted(self.request_widgets.keys())
        for req_id in sorted_ids:
            if req_id > removed_id:
                widget = self.request_widgets.pop(req_id)
                new_y = start_y + (req_id - removed_id - 1) * NEXT_REQUEST_PADDING
                widget.setGeometry(QtCore.QRect(0, new_y, 231, 161))
                self.request_widgets[req_id] = widget

        if self.request_widgets:
            last_widget = next(reversed(self.request_widgets.values()))
            self.next_request_y = last_widget.geometry().bottom() + NEXT_REQUEST_PADDING
        elif not self.request_widgets or len(self.request_widgets) == 1:
            self.next_request_y = 0
        else:
            self.next_request_y = 0

        self.ui.request_scrollArea_contents.setMinimumHeight(self.next_request_y)
        self.ui.request_scrollArea_contents.update()
