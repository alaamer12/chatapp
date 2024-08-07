from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QVBoxLayout
from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Optional
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
        self.ui.messages_scrollarea.hide()
        self.ui.no_rooms_label.show()
        self._create_rooms()
        self._connect_signals()

    def _connect_signals(self):
        self.ui.send_message_button_3.clicked.connect(self._on_send_clicked)

    def _create_room_widget(self, y_position: int) -> QWidget:
        room = QtWidgets.QWidget(self.ui.rooms_scrollArea_contents_3)
        room.setGeometry(QtCore.QRect(0, y_position, 251, 71))
        room.setObjectName("room")
        return room

    @staticmethod
    def _create_room_avatar(parent: QWidget) -> QWidget:
        avatar = QtWidgets.QWidget(parent)
        avatar.setGeometry(QtCore.QRect(0, 0, 81, 61))
        avatar.setStyleSheet("QWidget{\n"
                             "background-image:url(:/images/images/User_cicrle_duotone 72x72.png);\n"
                             " background-position: center;\n"
                             " background-repeat: no-repeat;\n"
                             "}")
        avatar.setObjectName("avatar")
        return avatar

    @staticmethod
    def _create_room_labels(parent: QWidget) -> QLabel:
        room_name_label = QtWidgets.QLabel(parent)
        room_name_label.setGeometry(QtCore.QRect(90, 10, 141, 13))  # Adjusted width
        room_name_label.setStyleSheet("QLabel{\n"
                                      "color: white;\n"
                                      "font-weight: 500\n"
                                      "}")
        room_name_label.setObjectName("room_name_label")

        room_username_label = QtWidgets.QLabel(parent)
        room_username_label.setGeometry(QtCore.QRect(90, 40, 141, 13))  # Adjusted width
        room_username_label.setStyleSheet("QLabel{\n"
                                          "color: #A0A0A0;\n"
                                          "}")
        room_username_label.setObjectName("room_username_label")

        return room_name_label, room_username_label

    @staticmethod
    def _create_room_button(parent: QWidget) -> QPushButton:
        button = QtWidgets.QPushButton(parent)
        button.setGeometry(QtCore.QRect(0, -10, 251, 81))
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setText("")
        button.setObjectName("room_clickable_button")
        return button

    def _create_room(self, name: str, username: str, y_position: int, room_id: int):
        room = self._create_room_widget(y_position)
        avatar = self._create_room_avatar(room)
        room_name_label, room_username_label = self._create_room_labels(room)
        room_clickable_button = self._create_room_button(room)

        avatar.raise_()
        room_name_label.raise_()
        room_username_label.raise_()

        room_name_label.setText(self._translate("MainWindow", name))
        room_username_label.setText(self._translate("MainWindow", username))

        self.rooms_widgets[room_id] = room

        room_clickable_button.clicked.connect(lambda: self._on_room_clicked(room_id))

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

    @staticmethod
    def _create_message_font() -> QtGui.QFont:
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        return font

    def _create_message_content(self, message_widget: QWidget, message_height: int, is_sender: bool, message) -> QLabel:
        message_content = QLabel(message_widget)
        message_content.setGeometry(QtCore.QRect(10, 10, 200, message_height - 40))  # Adjusted width and dynamic height

        font = self._create_message_font()
        message_content.setFont(font)

        message_content.setStyleSheet("QLabel{color: #E0E0E0; font-weight: 500;}")
        message_content.setObjectName("sender_message_content" if is_sender else "receiver_message_content")
        message_content.setText(self._translate("MainWindow", message))
        message_content.setWordWrap(True)

        return message_content

    @staticmethod
    def _create_date_font() -> QtGui.QFont:
        font = QtGui.QFont()
        font.setPointSize(7)
        return font

    def _create_message_date(self, message_widget: QWidget, message_height: int, is_sender: bool, date) -> QLabel:
        date_label = QLabel(message_widget)
        date_label.setGeometry(QtCore.QRect(10, message_height - 30, 200, 20))  # Adjusted width

        font = self._create_date_font()
        date_label.setFont(font)

        date_label.setStyleSheet("QLabel{color: #A0A0A0;}")
        date_label.setObjectName("sender_date" if is_sender else "receiver_date")
        date_label.setText(self._translate("MainWindow", date))

        return date_label

    @staticmethod
    def _estimate_message_height(message: str) -> int:
        estimated_lines = max(1, (len(message) // 50) + 1)
        return estimated_lines * 20 + 70

    def _create_message_widget(self, message: str, is_sender: bool, position: int) -> QWidget:
        message_height = self._estimate_message_height(message)
        message_widget = QWidget(self.ui.messages_scrollarea_contents)
        message_style = "QWidget{background-color: rgb(30, 30, 30); border-radius: 8px;}" if is_sender else "QWidget{background-color: #BB86FC; border-radius: 8px;}"
        message_widget.setStyleSheet(message_style)
        message_widget.setObjectName("sender_message" if is_sender else "receiver_message")
        message_widget.setGeometry(QtCore.QRect(10, position, 220, message_height))

        return message_widget

    def _create_message(self, message_id: int, message_count: int, message: str, date: str, position: int, is_sender: bool):
        message_height = self._estimate_message_height(message)
        message_widget = self._create_message_widget(message, is_sender, position)
        self._create_message_content(message_widget, message_height, is_sender, message)
        self._create_message_date(message_widget, message_height, is_sender, date)  # Changed method name

        self.messages_widgets[message_count] = message_widget

        # Ensure messages_scrollarea_contents has a layout
        if self.ui.messages_scrollarea_contents.layout() is None:
            self.ui.messages_scrollarea_contents.setLayout(QVBoxLayout())

        # Add the message widget to the layout
        self.ui.messages_scrollarea_contents.layout().addWidget(message_widget)

        return message_height

    def _load_messages(self, room_id: int):
        _messages = self.controller.handle_.loading_messages(room_id)
        messages = len(_messages)

        for i in range(messages):
            message = _messages[i]["Content"]
            date: datetime = _messages[i]["DateTime"]
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            is_sender = _messages[i]["UserID"] == _messages[i]["SenderID"]
            message_id = _messages[i]["MessageID"]

            message_height = self._create_message(message_id=message_id,
                                                  message_count=i,
                                                  message=message,
                                                  date=date,
                                                  position=self.next_message_position,
                                                  is_sender=is_sender)

            self.next_message_position += message_height + NEXT_MESSAGE_PADDING

        if messages > SAFE_MESSAGES_AREA_SIZE:
            self.ui.messages_scrollarea_contents.setMinimumHeight(self.next_message_position)

    def _on_send_clicked(self):
        message: str = self.ui.send_textinput_3.text().strip()
        if not message:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save the message into database
        message_id = self.controller.handle_.sending_message(message)

        # Update GUI
        self.ui.send_textinput_3.setText(self._translate("MainWindow", ""))
        message_height = self._create_message(message_id=message_id,
                                              message_count=len(self.messages_widgets),
                                              message=message,
                                              date=now,
                                              position=self.next_message_position,
                                              is_sender=True)

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
        self.ui.no_rooms_label.hide()
        self.ui.messages_scrollarea.show()
        self._clear_messages()
        self._load_messages(room_id)
