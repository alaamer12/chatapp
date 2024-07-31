from PyQt5.QtWidgets import QPushButton
from .base_page import BasePage
from collections import deque
from PyQt5 import QtCore, QtGui, QtWidgets
from typing import Iterable
import asyncio
from datetime import datetime
from .constants import NEXT_MESSAGE_PADDING, NEXT_ROOM_PADDING


class Chatting(BasePage):
    def __init__(self, controller, ui):
        super().__init__(controller, ui)
        self.next_room_position = 0
        self.next_message_position = 0
        self.stack = deque()
        self.room_clickable_button: QPushButton = None

    def initialize_page(self):
        self.ui.messages_scrollarea.hide()
        self.ui.no_rooms_label.show()
        # self._create_room("username", "name", self.next_room_position)
        # self._create_messages()
        # self._load_roams()
        self._connect_signals()

    @staticmethod
    def _translate(context, source_text):
        _translate = QtCore.QCoreApplication.translate
        return _translate(context, source_text)

    async def _load_roams(self):
        pass

    def _connect_tabs_signals(self):
        self.ui.chatting_chatting_button.clicked.connect(
            lambda: self.controller.handle_tabs_clicked(self.ui.chatting_chatting_button.text().strip()))
        self.ui.chatting_exit_button.clicked.connect(
            lambda: self.controller.handle_tabs_clicked(self.ui.chatting_exit_button.text().strip()))
        self.ui.chatting_requests_button.clicked.connect(
            lambda: self.controller.handle_tabs_clicked(self.ui.chatting_requests_button.text().strip()))
        self.ui.chatting_settings_button.clicked.connect(
            lambda: self.controller.handle_tabs_clicked(self.ui.chatting_settings_button.text().strip()))

    def _connect_signals(self):
        self._connect_tabs_signals()
        self.room_clickable_button.clicked.connect(self._on_room_clicked)
        self.ui.send_message_button.clicked.connect(self._on_send_clicked)

    def _create_room(self, name: str, username: str, position):
        self.room = QtWidgets.QWidget(self.ui.rooms_scrollArea_contents)
        self.room.setGeometry(QtCore.QRect(0, position + 0, 251, 71))
        self.room.setObjectName("room")
        self.avatar = QtWidgets.QWidget(self.room)
        self.avatar.setGeometry(QtCore.QRect(0, position + 0, 81, 61))

        self.avatar.setStyleSheet("QWidget{\n"
                                  "background-image:url(:/images/images/User_cicrle_duotone 72x72.png);\n"
                                  " background-position: center;\n"
                                  "background-size: 50px;\n"
                                  " background-repeat: no-repeat;\n"
                                  "}")

        self.avatar.setObjectName("avatar")

        self.room_name_label = QtWidgets.QLabel(self.room)
        self.room_name_label.setGeometry(QtCore.QRect(90, position + 10, 47, 13))
        self.room_name_label.setStyleSheet("QLabel{\n"
                                           "color: white;\n"
                                           "font-weight: 500\n"
                                           "}")
        self.room_name_label.setObjectName("room_name_label")

        self.room_username_label = QtWidgets.QLabel(self.room)
        self.room_username_label.setGeometry(QtCore.QRect(90, position + 40, 47, 13))

        self.room_username_label.setStyleSheet("QLabel{\n"
                                               "color: #A0A0A0;\n"
                                               "}")

        self.room_username_label.setObjectName("room_username_label")

        self.room_clickable_button = QtWidgets.QPushButton(self.room)
        self.room_clickable_button.setGeometry(QtCore.QRect(0, position + -10, 251, 81))
        self.room_clickable_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.room_clickable_button.setText("")
        self.room_clickable_button.setObjectName("room_clickable_button")
        self.room_clickable_button.raise_()

        self.avatar.raise_()
        self.room_name_label.raise_()
        self.room_username_label.raise_()

        self.room_name_label.setText(self._translate("MainWindow", name))
        self.room_username_label.setText(self._translate("MainWindow", username))

    def _create_rooms(self):
        ordered_rooms: Iterable = self.controller.get_rooms()
        name, username = self.controller.get_room_metadata()
        length = len(ordered_rooms)
        for i in range(length):
            self._create_room(name, username, position=self.next_room_position)
            self.next_room_position += NEXT_ROOM_PADDING

    def _create_sender_message(self, message, date, position: int):
        self.sender_message = QtWidgets.QWidget(self.ui.messages_scrollarea_contents)
        self.sender_message.setGeometry(QtCore.QRect(10, position + 110, 91, 41))
        self.sender_message.setStyleSheet("QWidget{\n"
                                          "background-color: rgb(30, 30, 30);\n"
                                          "border-radius: 8px\n"
                                          "}")
        self.sender_message.setObjectName("sender_message")
        self.sender_message_content = QtWidgets.QLabel(self.sender_message)
        self.sender_message_content.setGeometry(QtCore.QRect(0, position + 10, 51, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(62)
        font.setStrikeOut(False)
        self.sender_message_content.setFont(font)
        self.sender_message_content.setStyleSheet("QLabel{\n"
                                                  "color: #E0E0E0;\n"
                                                  "font-weight: 500;\n"
                                                  "}")
        self.sender_message_content.setObjectName("sender_message_content")
        self.sender_message_date = QtWidgets.QLabel(self.sender_message)
        self.sender_message_date.setGeometry(QtCore.QRect(40, position + 30, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(5)
        self.sender_message_date.setFont(font)
        self.sender_message_date.setStyleSheet("color: white")
        self.sender_message_date.setObjectName("sender_message_date")

        self.sender_message_content.setText(self._translate("MainWindow", message))
        self.sender_message_date.setText(self._translate("MainWindow", date))

    def _create_receiver_message(self, message, date, position):
        self.receiver_message = QtWidgets.QWidget(self.ui.messages_scrollarea_contents)
        self.receiver_message.setGeometry(QtCore.QRect(320, position + 50, 171, 41))
        self.receiver_message.setStyleSheet("QWidget{\n"
                                            "background-color: #BB86FC;\n"
                                            "border-radius: 8px\n"
                                            "}")
        self.receiver_message.setObjectName("receiver_message")
        self.receiver_message_content = QtWidgets.QLabel(self.receiver_message)
        self.receiver_message_content.setGeometry(QtCore.QRect(-10, position + 10, 171, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(62)
        font.setStrikeOut(False)
        self.receiver_message_content.setFont(font)
        self.receiver_message_content.setStyleSheet("QLabel{\n"
                                                    "color: #E0E0E0;\n"
                                                    "font-weight: 500;\n"
                                                    "}")
        self.receiver_message_content.setObjectName("receiver_message_content")
        self.receiver_message_date = QtWidgets.QLabel(self.receiver_message)
        self.receiver_message_date.setGeometry(QtCore.QRect(140, position + 30, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(5)
        self.receiver_message_date.setFont(font)
        self.receiver_message_date.setStyleSheet("color: white")
        self.receiver_message_date.setObjectName("receiver_message_date")

        self.receiver_message_content.setText(self._translate("MainWindow", message))
        self.receiver_message_date.setText(self._translate("MainWindow", date))

    def _create_message(self, *, message, date, position, is_sender: bool):
        if is_sender:
            self._create_sender_message(message, date, position)
        else:
            self._create_receiver_message(message, date, position)


    async def _load_messages(self):
        _messages: Iterable = await self.controller.get_messages()
        for message in len(_messages):
            self._create_message(message=message, date=message.date, position=self.next_message_position ,is_sender=message.is_sender)
            self.next_message_position += NEXT_MESSAGE_PADDING







    def _on_room_clicked(self):
        pass

    def _load_message(self):
        pass

    async def _update_user_status(self):
        # Retrieve the user's status
        status = await self.controller.get_user_status()

        # Update the status in the UI based on the retrieved status
        if status == 'online':
            self.ui.message_box_status.setText(self._translate("MainWindow", "Online"))
            self.ui.message_box_status.setStyleSheet("color: green;")  # Change color to green for online
        elif status == 'offline':
            self.ui.message_box_status.setText(self._translate("MainWindow", "Offline"))
            self.ui.message_box_status.setStyleSheet("color: red;")  # Change color to red for offline
        await asyncio.sleep(1)


    async def _on_send_clicked(self):
        message: str = self.ui.send_textinput.text().strip()
        if message:
            # Get Date Now
            now = datetime.now()

            # Save to Database
            await self.controller.send_message(message)

            # Set TextInput
            self.ui.send_textinput.setText(self._translate("MainWindow", ""))

            # Create the new Message
            self.next_message_position += NEXT_MESSAGE_PADDING
            self._create_message(message=message, date=now, position=self.next_message_position, is_sender=True)
