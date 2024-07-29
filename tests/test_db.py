import pytest
import mysql.connector
import uuid
from datetime import datetime
from model.db import DB

TEST_DB_NAME = 'testing_db'
TEST_DB_USER = 'root'
TEST_DB_PASSWORD = 'root'
TEST_DB_LOCALHOST = 'localhost'


@pytest.fixture(scope='function')
def db():
    # Create a new connection and database for each test
    connection = mysql.connector.connect(
        host='localhost',
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME}")
    connection.database = TEST_DB_NAME

    # Drop and recreate tables to ensure a clean state
    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("DROP TABLE IF EXISTS Friends")
    cursor.execute("DROP TABLE IF EXISTS Message")

    # Replace with actual table creation code
    cursor.execute(
        """CREATE TABLE Users (UserID VARCHAR(255) PRIMARY KEY, 
        FriendID VARCHAR(600), UserName VARCHAR(255),
        Password VARCHAR(80), IsOnline BOOLEAN, IsAccept BOOLEAN, 
        FOREIGN KEY (FriendID) REFERENCES Users(UserID))
        """)
    cursor.execute(
        "CREATE TABLE Friends (RoomID VARCHAR(255), Name VARCHAR(255), UserID VARCHAR(255), PRIMARY KEY (RoomID, Name, UserID))")
    cursor.execute(
        "CREATE TABLE Message (MessageID VARCHAR(255) PRIMARY KEY, UserID VARCHAR(255), Content TEXT, DateTime DATETIME, RoomID VARCHAR(255))")
    cursor.close()

    db_instance = DB(localhost=TEST_DB_LOCALHOST, user=TEST_DB_USER, password=TEST_DB_PASSWORD, database=TEST_DB_NAME)
    yield db_instance

    # Cleanup: Drop database after each test
    db_instance.close()
    connection = mysql.connector.connect(
        host='localhost',
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD
    )
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cursor.close()
    connection.close()


def generate_unique_id():
    return str(uuid.uuid4())


friend_id = generate_unique_id()


class TestDatabase:

    def test_create_tables(self, db):
        tables = db.get_all_tables()
        assert 'users' in tables
        assert 'message' in tables
        assert 'friends' in tables

    def test_add_to(self, db):
        # Generate unique IDs for the users
        user_id = generate_unique_id()

        # Add a record for the friend first
        db.add_to('Users', UserID=friend_id, UserName='Friend Name', Password='hashed_password', IsOnline=1, IsAccept=1)

        db.add_to('Users', UserID=user_id, FriendID=friend_id, UserName='Test User', Password='hashed_password',
                  IsOnline=1, IsAccept=1)

        db.add_to('Friends', RoomID='room1', Name='Friend1', UserID=user_id)

        result = db.get_all('Friends', 'RoomID', 'Name', 'UserID')
        assert ('room1', 'Friend1', user_id) in result

    def test_update_at(self, db):
        user_id = generate_unique_id()

        # Add a record for the friend first
        db.add_to('Users', UserID=user_id, UserName='Test User', Password='hashed_password',
                  IsOnline=1, IsAccept=1)

        # Update it
        new_username = 'Updated User'
        db.update_at('Users', condition=f"UserID='{user_id}'", UserName=new_username)

        result = db.get_all('Users', 'UserID', 'UserName', 'IsOnline', 'IsAccept')
        assert (user_id, new_username, 1, 1) in result

    def test_get_last_by(self, db):
        user_id = generate_unique_id()
        db.add_to('Users', UserID=friend_id, UserName='Friend Name', Password='hashed_password', IsOnline=1, IsAccept=1)

        db.add_to('Users', UserID=user_id, FriendID=friend_id, UserName='Test User', Password='hashed_password',
                  IsOnline=1, IsAccept=1)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Add a message after adding the user
        db.add_to('Message', MessageID=generate_unique_id(), UserID=user_id, Content='Test Message',
                  DateTime=timestamp,
                  RoomID='room1')

        # Retrieve the last message
        result = db.get_last_by('room1', 'Message', 'MessageID', 'Content', 'DateTime')
        assert result is not None
        assert result[1] == 'Test Message'  # Adjusted as per actual function return

    def test_get_all(self, db):
        user_id = generate_unique_id()
        db.add_to('Users', UserID=friend_id, UserName='Friend Name', Password='hashed_password', IsOnline=1, IsAccept=1)

        db.add_to('Users', UserID=user_id, FriendID=friend_id, UserName='Test User', Password='hashed_password',
                  IsOnline=1, IsAccept=1)

        # Then add friends data
        db.add_to('Friends', RoomID='room1', Name='Friend1', UserID=user_id)

        # Retrieve and check friends data
        result = db.get_all('Friends', 'RoomID', 'Name', 'UserID')
        assert ('room1', 'Friend1', user_id) in result

    def test_is_user_online(self, db):
        user_id = generate_unique_id()
        db.add_to('Users', UserID=friend_id, UserName='Friend Name', Password='hashed_password', IsOnline=1, IsAccept=1)

        db.add_to('Users', UserID=user_id, FriendID=friend_id, UserName='Test User', Password='hashed_password',
                  IsOnline=1, IsAccept=1)
        result = db.is_user_online(user_id)
        assert result is True

