from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QVBoxLayout
from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Optional
import asyncio
from datetime import datetime
from .base_page import BasePage
from .constants import NEXT_MESSAGE_PADDING, NEXT_ROOM_PADDING, SAFE_MESSAGES_AREA_SIZE, SAFE_ROOMS_AREA_SIZE


class Chatting(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)
        self.next_room_position = 0
        self.next_message_position = 0
        self.room_clickable_button: Optional[QPushButton] = None
        self.user: Optional[str] = None
        self.rooms_widgets: dict[int, QWidget] = {}
        self.messages_widgets: dict[int, QWidget] = {}
        self._clear_messages()
        self.initialize_page()

    def initialize_page(self):
        self.user = self.controller.get_.current_user()
        self.ui.messages_scrollarea.hide()
        self.ui.no_rooms_label.show()
        self._create_rooms()
        self._connect_signals()


    def _connect_signals(self):
        self.ui.send_message_button_3.clicked.connect(self._on_send_clicked)

    def _create_room(self, name: str, username: str, y_position: int, room_id: int):
        self.room = QtWidgets.QWidget(self.ui.rooms_scrollArea_contents_3)
        self.room.setGeometry(QtCore.QRect(0, y_position, 251, 71))
        self.room.setObjectName("room")

        self.avatar = QtWidgets.QWidget(self.room)
        self.avatar.setGeometry(QtCore.QRect(0, 0, 81, 61))
        self.avatar.setStyleSheet("QWidget{\n"
                                  "background-image:url(:/images/images/User_cicrle_duotone 72x72.png);\n"
                                  " background-position: center;\n"
                                  " background-repeat: no-repeat;\n"
                                  "}")
        self.avatar.setObjectName("avatar")

        self.room_name_label = QtWidgets.QLabel(self.room)
        self.room_name_label.setGeometry(QtCore.QRect(90, 10, 141, 13))  # Adjusted width
        self.room_name_label.setStyleSheet("QLabel{\n"
                                           "color: white;\n"
                                           "font-weight: 500\n"
                                           "}")
        self.room_name_label.setObjectName("room_name_label")

        self.room_username_label = QtWidgets.QLabel(self.room)
        self.room_username_label.setGeometry(QtCore.QRect(90, 40, 141, 13))  # Adjusted width
        self.room_username_label.setStyleSheet("QLabel{\n"
                                               "color: #A0A0A0;\n"
                                               "}")
        self.room_username_label.setObjectName("room_username_label")

        self.room_clickable_button = QtWidgets.QPushButton(self.room)
        self.room_clickable_button.setGeometry(QtCore.QRect(0, -10, 251, 81))
        self.room_clickable_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.room_clickable_button.setText("")
        self.room_clickable_button.setObjectName("room_clickable_button")
        self.room_clickable_button.raise_()

        self.avatar.raise_()
        self.room_name_label.raise_()
        self.room_username_label.raise_()

        self.room_name_label.setText(self._translate("MainWindow", name))
        self.room_username_label.setText(self._translate("MainWindow", username))

        self.rooms_widgets[room_id] = self.room

        self.room_clickable_button.clicked.connect(lambda: self._on_room_clicked(room_id))

    def _create_rooms(self):
        self.rooms: list[dict] = self.controller.handle_.rooms()
        rooms = len(self.rooms)
        if not any(len(d) == 0 for d in self.rooms):
            for i in range(rooms):
                self._create_room(name=self.rooms[i]["UserName"],
                                  username=self.rooms[i]["FriendID"],
                                  y_position=self.next_room_position,
                                  room_id=self.rooms[i]["RoomID"])
                self.next_room_position += NEXT_ROOM_PADDING
        if rooms > SAFE_ROOMS_AREA_SIZE:
            self.ui.rooms_scrollArea_contents.setMinimumHeight(self.next_room_position)

    def _create_message(self, message_id, message: str, date: str, position: int, is_sender: bool):
        # Estimate the height based on message length
        estimated_lines = max(1, (len(message) // 50) + 1)
        message_height = estimated_lines * 20 + 70  # 20 pixels per line + 60 for padding and date

        # Create the message widget
        message_widget = QWidget(self.ui.messages_scrollarea_contents)
        message_style = "QWidget{background-color: rgb(30, 30, 30); border-radius: 8px;}" if is_sender else "QWidget{background-color: #BB86FC; border-radius: 8px;}"
        message_widget.setStyleSheet(message_style)
        message_widget.setObjectName("sender_message" if is_sender else "receiver_message")

        # Create the message content label
        message_content = QLabel(message_widget)
        message_content.setGeometry(QtCore.QRect(10, 10, 200, message_height - 40))  # Adjusted width and dynamic height
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        message_content.setFont(font)
        message_content.setStyleSheet("QLabel{color: #E0E0E0; font-weight: 500;}")
        message_content.setObjectName("sender_message_content" if is_sender else "receiver_message_content")
        message_content.setText(self._translate("MainWindow", message))
        message_content.setWordWrap(True)  # Enable word wrapping

        # Create the date label
        message_date = QLabel(message_widget)
        message_date.setGeometry(
            QtCore.QRect(10, message_height - 20, 200, 15))  # Adjusted position based on dynamic height
        font.setPointSize(7)
        message_date.setFont(font)
        message_date.setStyleSheet("color: white")
        message_date.setObjectName("sender_message_date" if is_sender else "receiver_message_date")
        message_date.setText(self._translate("MainWindow", date))

        self.messages_widgets[message_id] = message_widget

        # Add the message widget to the layout
        self.ui.messages_scrollarea_contents.layout().addWidget(message_widget)

        return message_height  # Return the height to adjust the position of the next message

    def _load_messages(self, room_id: int):
        _messages = self.controller.handle_.loading_messages(room_id)
        messages = len(_messages)
        for i in range(messages):
            message = _messages[i]["Content"]
            date: datetime = _messages[i]["DateTime"]
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            is_sender = _messages[i]["UserID"] == _messages[i]["SenderID"]
            message_height = self._create_message(message_id=i, message=message, date=date,
                                                  position=self.next_message_position,
                                                  is_sender=is_sender)
            self.next_message_position += message_height + NEXT_MESSAGE_PADDING
        if messages > SAFE_MESSAGES_AREA_SIZE:
            self.ui.messages_scrollarea_contents.setMinimumHeight(self.next_message_position)

    async def _update_user_status(self, user):
        status_text, status_color = self.controller.get_.user_status(user)
        self.ui.message_box_status.setText(self._translate("MainWindow", status_text))
        self.ui.message_box_status.setStyleSheet(f"color: {status_color};")
        await asyncio.sleep(1)

    def _on_send_clicked(self):
        print("clicked")
        message: str = self.ui.send_textinput_3.text().strip()
        if message:
            print(message)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save the message into database
            self.controller.handle_.sending_message(len(self.messages_widgets), message)

            # Update GUI
            self.ui.send_textinput_3.setText(self._translate("MainWindow", ""))
            message_height = self._create_message(message_id=len(self.messages_widgets), message=message, date=now,
                                                  position=self.next_message_position, is_sender=True)
            self.next_message_position += message_height + NEXT_MESSAGE_PADDING
            self.ui.messages_scrollarea_contents.setMinimumHeight(self.next_message_position)

    def _clear_messages(self):
        # Clear existing messages
        if self.ui.messages_scrollarea_contents.layout() is not None:
            while self.ui.messages_scrollarea_contents.layout().count():
                item = self.ui.messages_scrollarea_contents.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # Create a new layout if not exists
        if self.ui.messages_scrollarea_contents.layout() is None:
            layout = QVBoxLayout(self.ui.messages_scrollarea_contents)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

        self.next_message_position = 0

    def _on_room_clicked(self, room_id):
        # Open the messages of the room
        print(f"Room {room_id} clicked")
        self.ui.no_rooms_label.hide()
        self.ui.messages_scrollarea.show()
        self._clear_messages()
        self._load_messages(room_id)
