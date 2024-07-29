DB_LOCALHOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'chat_db'


HOST = '127.0.0.1'
PORT = 9090


Users_METADATA = [
    'UserID VARCHAR(255) PRIMARY KEY',
    'FriendID VARCHAR(255)',
    'UserName VARCHAR(255) NOT NULL',
    'Password VARCHAR(80) NOT NULL',
    'IsOnline BOOLEAN NOT NULL',
    'IsAccept BOOLEAN NOT NULL',
    'FOREIGN KEY (FriendID) REFERENCES Users(UserID)'
]

Message_METADATA = [
    'MessageID VARCHAR(550) PRIMARY KEY',
    'UserID VARCHAR(255) NOT NULL',
    'Content TEXT',
    'DateTime TIMESTAMP NOT NULL',
    'RoomID VARCHAR(255) NOT NULL',
    'FOREIGN KEY (UserID) REFERENCES Users(UserID)'
]

Friends_METADATA = [
    'RoomID VARCHAR(255) PRIMARY KEY',
    'Name VARCHAR(255) NOT NULL',
    'UserID VARCHAR(255) NOT NULL',
    'FOREIGN KEY (UserID) REFERENCES Users(UserID)'
]