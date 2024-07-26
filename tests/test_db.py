import pytest
import mysql.connector
from model.db import DB
from datetime import datetime
TEST_DB_NAME = 'test_db'
TEST_DB_USER = 'root'
TEST_DB_PASSWORD = 'root'


@pytest.fixture(scope='module')
def db():
    connection = mysql.connector.connect(
        host='localhost',
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME}")
    connection.database = TEST_DB_NAME
    cursor.close()

    db_instance = DB(localhost='localhost', user=TEST_DB_USER, password=TEST_DB_PASSWORD, database=TEST_DB_NAME)
    yield db_instance

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


def test_create_tables(db):
    tables = db.get_all_tables()
    assert 'Users' in tables
    assert 'Message' in tables
    assert 'Friends' in tables


def test_add_to(db):
    db.add_to('Users', UserID='user1', UserName='Test User', Password='hashed_password', IsOnline=1, IsAccept=1)
    result = db.get_all('Users', 'UserID', 'UserName')
    assert ('user1', 'Test User') in result


def test_get_last(db):
    db.add_to('Message', MessageID='msg1', UserID='user1', Content='Test Message', DateTime=datetime.now(),
              RoomID='room1')
    result = db.get_last('room1', 'Message', 'MessageID', 'Content', 'DateTime')
    assert result[0] == 'msg1'
    assert result[1] == 'Test Message'


def test_get_all(db):
    db.add_to('Friends', RoomID='room1', Name='Friend1', UserID='user1')
    result = db.get_all('Friends', 'RoomID', 'Name')
    assert ('room1', 'Friend1') in result


def test_is_user_online(db):
    db.add_to('Users', UserID='user1', UserName='Test User', Password='hashed_password', IsOnline=1, IsAccept=1)
    result = db.is_user_online('user1')
    assert result is True

    db.add_to('Users', UserID='user2', UserName='Another User', Password='hashed_password', IsOnline=0, IsAccept=1)
    result = db.is_user_online('user2')
    assert result is False
