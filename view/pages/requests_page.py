from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton
from .base_page import BasePage
from typing import Optional, Dict
from .constants import NEXT_REQUEST_PADDING, SAFE_REQUESTS_AREA_SIZE


class Requests(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)
        self.accept_button: Optional[QPushButton] = None
        self.decline_button: Optional[QPushButton] = None
        self.next_request_y = 0
        self.request_widgets: Dict[int, QtWidgets.QWidget] = {}
        self.initialize_page()

    def initialize_page(self):
        print("Initializing Requests Page...")
        self._initialize_layout()
        self._populate_requests()
        self._connect_signals()

    def _initialize_layout(self):
        print("Initializing Layout...")
        if not self.ui.request_scrollArea_contents.layout():
            self.ui.request_scrollArea_contents.setLayout(QtWidgets.QVBoxLayout())

    def _connect_signals(self):
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

    def _create_request_widget(self, y_position: int, request_id: int) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget(self.ui.request_scrollArea_contents)
        widget.setGeometry(QtCore.QRect(0, y_position, 231, 161))
        widget.setObjectName(f"request_{request_id}")
        widget.setProperty("request_id", request_id)  # Store request_id as a property
        return widget

    @staticmethod
    def _create_request_labels(widget: QtWidgets.QWidget, fullname: str, date: str):
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

        return label_request, name_label, date_label

    def _create_buttons(self, widget: QtWidgets.QWidget, request_id: int):
        button_container = QtWidgets.QWidget(widget)
        button_container.setGeometry(QtCore.QRect(20, 110, 181, 41))
        button_layout = QtWidgets.QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        accept_button = self._create_button("Accept", "#444444", "#E0E0E0", button_container)
        decline_button = self._create_button("Decline", "#CF6679", "#E0E0E0", button_container)

        button_layout.addWidget(accept_button)
        button_layout.addItem(
            QtWidgets.QSpacerItem(8, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        button_layout.addWidget(decline_button)

        accept_button.clicked.connect(lambda: self._on_request_action(request_id, "accept"))
        decline_button.clicked.connect(lambda: self._on_request_action(request_id, "decline"))

    @staticmethod
    def _create_button(text: str, background_color: str, text_color: str,
                       parent: QtWidgets.QWidget) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(text, parent)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet(
            f"background-color: {background_color}; color: {text_color}; border-radius: 5px; width: 70px; height: 35px;")
        return button

    @staticmethod
    def _create_username_label(widget: QtWidgets.QWidget, username: str):
        username_label = QtWidgets.QLabel(username, widget)
        username_label.setGeometry(QtCore.QRect(10, 50, 211, 16))
        username_label.setStyleSheet("color: #A0A0A0")
        return username_label

    @staticmethod
    def _create_separator(widget: QtWidgets.QWidget):
        separator = QtWidgets.QFrame(widget)
        separator.setGeometry(QtCore.QRect(0, 150, 231, 20))
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        return separator

    def _create_request(self, fullname, username, date: str, y_position: int, request_id: int):
        widget = self._create_request_widget(y_position, request_id)
        self._create_request_labels(widget, fullname, date)
        self._create_buttons(widget, request_id)
        self._create_username_label(widget, username)
        self._create_separator(widget)

        self.request_widgets[request_id] = widget

    def _populate_requests(self):
        self._clear_requests()
        self.requests: list[dict] = self.controller.handle_.requests()
        num_requests = len(self.requests)
        if num_requests > 0:
            for i in range(num_requests):
                self._create_request(
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
        # Retrieve the request_id directly from the widget
        if request_id in self.request_widgets:
            userid = next((req["UserID"] for req in self.requests if req["RequestID"] == request_id), None)
            if userid:
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
        self._adjust_widget_positions(removed_id, start_y)
        self._update_scroll_area_height()

    def _adjust_widget_positions(self, removed_id: int, start_y: int):
        sorted_ids = sorted(self.request_widgets.keys())
        for req_id in sorted_ids:
            if req_id > removed_id:
                self._move_widget(req_id, start_y)

    def _move_widget(self, req_id: int, start_y: int):
        widget = self.request_widgets.pop(req_id)
        new_y = start_y + (req_id - 1) * NEXT_REQUEST_PADDING
        widget.setGeometry(QtCore.QRect(0, new_y, 231, 161))
        self.request_widgets[req_id] = widget

    def _update_scroll_area_height(self):
        if self.request_widgets:
            self._set_next_request_y_from_last_widget()
        else:
            self.next_request_y = 0

        self.ui.request_scrollArea_contents.setMinimumHeight(self.next_request_y)
        self.ui.request_scrollArea_contents.update()

    def _set_next_request_y_from_last_widget(self):
        last_widget = next(reversed(self.request_widgets.values()))
        self.next_request_y = last_widget.geometry().bottom() + NEXT_REQUEST_PADDING
