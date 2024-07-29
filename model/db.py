import contextlib
import mysql.connector
from typing import List, Tuple, Optional
import sys
from .helpers.constants import Users_METADATA, Friends_METADATA, Message_METADATA


class DB:
    def __init__(self, *, localhost: str, user: str, password: Optional[str],
                 database: Optional[str] = None):
        self.database = database

        self.__conn = mysql.connector.connect(
            host=localhost,
            user=user,
            password=password,
        )
        self.__cursor = self.__conn.cursor()

        if self.database:
            self.__create_database()

        self.__conn.database = self.database
        self.__create_tables()
        self._room_id = ""

    def __create_tables(self) -> None:
        tables = {
            'Users': Users_METADATA,
            'Message': Message_METADATA,
            'Friends': Friends_METADATA
        }
        for table_name, columns in tables.items():
            columns_str = ', '.join(columns)
            with self.connection() as cursor:
                cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})')

    def __create_database(self) -> None:
        try:
            self.__cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        except mysql.connector.Error as err:
            print(f"Failed creating database: {err}")
            sys.exit(1)

    @contextlib.contextmanager
    def connection(self):
        try:
            yield self.__cursor
        except Exception as e:
            self.__conn.rollback()
            print(f"Error occurred: {e}")
            raise
        else:
            self.__conn.commit()

    @property
    def room_id(self) -> str:
        return self._room_id

    @room_id.setter
    def room_id(self, room_id: str) -> None:
        self._room_id = room_id

    def get_all_tables(self) -> List[str]:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
        self.__cursor.execute(query, (self.__conn.database,))
        tables = self.__cursor.fetchall()
        return [table[0] for table in tables]

    def add_to(self, table: str, **columns):
        columns_str: str = ', '.join(columns.keys())
        placeholders = ', '.join('%s' for _ in columns)
        values = tuple(columns.values())
        query = f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})'

        with self.connection() as cursor:
            cursor.execute(query, values)

    def update_at(self, table: str, *, condition, **columns):
        set_clause = ', '.join(f"{col} = %s" for col in columns.keys())

        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

        values = tuple(columns.values())

        with self.connection() as cursor:
            cursor.execute(query, values)

    def get_last_by(self, room_id: str, table: str, *columns) -> Optional[Tuple]:
        # Ensure 'RoomID' is in the table's columns
        if 'RoomID' not in [col.split(' ')[0] for col in self.__get_table_metadata(table)]:
            raise ValueError(f"Table {table} does not have a RoomID column")

        # Ensure 'DateTime' is in the table's columns if ordering by it
        if 'DateTime' in columns:
            columns_str = ', '.join(columns)
            query = f'SELECT {columns_str} FROM {table} WHERE RoomID = %s ORDER BY DateTime DESC LIMIT 1'
        else:
            columns_str = ', '.join(columns)
            query = f'SELECT {columns_str} FROM {table} WHERE RoomID = %s LIMIT 1'

        with self.connection() as cursor:
            cursor.execute(query, (room_id,))
            result: Optional[Tuple] = cursor.fetchone()

        return result if result else None

    def get_all(self, table: str, *columns) -> List[Tuple]:
        if not columns:
            # Get all the data in the table
            query = f'SELECT * FROM {table}'
        else:
            # Ensure requested columns are valid for the table
            valid_columns = [col.split(' ')[0] for col in self.__get_table_metadata(table)]
            for column in columns:
                if column not in valid_columns:
                    raise ValueError(f"Column {column} does not exist in table {table}")

            columns_str = ', '.join(columns)
            query = f'SELECT {columns_str} FROM {table}'

        with self.connection() as cursor:
            cursor.execute(query)
            result: List[Tuple] = cursor.fetchall()

        return result if result else []

    def is_user_online(self, user_id: str) -> bool:
        query = "SELECT IsOnline FROM Users WHERE UserID = %s"
        self.__cursor.execute(query, (user_id,))
        result = self.__cursor.fetchone()
        return bool(result[0]) if result else False

    def __get_table_metadata(self, table_name: str) -> List[str]:
        query = f"SHOW COLUMNS FROM {table_name}"
        self.__cursor.execute(query)
        columns = self.__cursor.fetchall()
        return [col[0] for col in columns]

    def close(self):
        if self.__conn:
            self.__conn.close()
