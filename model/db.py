import contextlib
import mysql.connector
from typing import List, Tuple, Optional

Users_METADATA = [
    'UserID VARCHAR(255) PRIMARY KEY',  # Changed TEXT to VARCHAR(255)
    'UserName VARCHAR(255) NOT NULL',
    'Password VARCHAR(255) NOT NULL',
    'IsOnline INTEGER NOT NULL',
    'IsAccept INTEGER NOT NULL'
]

Message_METADATA = [
    'MessageID VARCHAR(255) PRIMARY KEY',  # Changed TEXT to VARCHAR(255)
    'UserID VARCHAR(255) NOT NULL',
    'Content TEXT',
    'DateTime TIMESTAMP NOT NULL',  # Changed TEXT to TIMESTAMP
    'RoomID VARCHAR(255) NOT NULL',
    'FOREIGN KEY (UserID) REFERENCES Users(UserID)'
]

Friends_METADATA = [
    'RoomID VARCHAR(255) PRIMARY KEY',  # Changed TEXT to VARCHAR(255)
    'Name VARCHAR(255) NOT NULL',
    'UserID VARCHAR(255) NOT NULL',
    'FOREIGN KEY (UserID) REFERENCES Users(UserID)'
]


class DB:
    def __init__(self, *, localhost: str = 'localhost', user: str = 'root', password: str = 'root',
                 database: Optional[str] = None):
        self.__conn = mysql.connector.connect(
            host=localhost,
            user=user,
            password=password,
            database=database
        )
        self.__cursor = self.__conn.cursor()
        self.__create_tables()
        self._room_id = ""

    def __create_tables(self) -> None:
        tables = {
            'Users': Users_METADATA,
            'Message': Message_METADATA,
            'Friends': Friends_METADATA
        }
        for table_name, columns in tables.items():
            columns_str: str = ', '.join(columns)
            with self.connection() as cursor:
                cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})')

    @contextlib.contextmanager
    def connection(self):
        try:
            yield self.__cursor
        except Exception as e:
            self.__conn.rollback()
            raise e
        else:
            self.__conn.commit()

    @property
    def room_id(self) -> str:
        return self._room_id

    @room_id.setter
    def room_id(self, room_id: str) -> None:
        self._room_id = room_id

    def get_all_tables(self):
        # If MYSQL
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
        self.__cursor.execute(query, (self.__conn.database,))
        tables = self.__cursor.fetchall()
        return [table[0] for table in tables]

        # IF SQLITE3
        # self.__cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # tables = self.__cursor.fetchall()
        # return [table[0] for table in tables]

    def add_to(self, table: str, **columns):
        columns_str: str = ', '.join(columns.keys())
        placeholders: str = ', '.join('%s' * len(columns))  # Changed from '?' to '%s'
        values = tuple(columns.values())
        query = f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})'

        with self.connection() as cursor:
            cursor.execute(query, values)

    def get_last(self, room_id: str, table: str, *columns) -> Optional[Tuple]:
        columns_str = ', '.join(columns)
        query = f'SELECT {columns_str} FROM {table} WHERE RoomID = %s ORDER BY DateTime DESC LIMIT 1'
        self.__cursor.execute(query, (room_id,))
        result: Optional[Tuple] = self.__cursor.fetchone()
        return result if result else None

    def get_all(self, table: str, *columns) -> List[Tuple]:
        columns_str = ', '.join(columns)
        query = f'SELECT {columns_str} FROM {table}'
        self.__cursor.execute(query)
        result: List[Tuple] = self.__cursor.fetchall()
        return result if result else []

    def is_user_online(self, user_id: str) -> bool:
        query = "SELECT IsOnline FROM Users WHERE UserID = %s"
        self.__cursor.execute(query, (user_id,))
        result = self.__cursor.fetchone()
        return bool(result[0]) if result else False

    def close(self):
        if self.__conn:
            self.__conn.close()
