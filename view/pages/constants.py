from enum import IntEnum, Enum



NEXT_ROOM_PADDING = 71
NEXT_MESSAGE_PADDING = 30
NEXT_REQUEST_PADDING = 161

SAFE_REQUESTS_AREA_SIZE = 3
SAFE_ROOMS_AREA_SIZE = 6
SAFE_MESSAGES_AREA_SIZE = 4  # 10

class Pages(IntEnum):
    LOGIN = 0
    REGISTRATION = 1
    CHATTING = 2
    SETTINGS = 3
    REQUESTS = 4

class UserStatus(Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    AWAY = "Away"
    BUSY = "Busy"
