from .db import DB
from .server import Server
from .client import Client
from .helpers.constants import HOST, PORT, DB_LOCALHOST, DB_NAME, DB_USER, DB_PASSWORD
from datetime import datetime


class Model:
    def __init__(self):
        self.sever = Server(host=HOST, port=PORT)
        self.client = Client(host=HOST, port=PORT)
        self.db = DB(localhost=DB_LOCALHOST, user=DB_USER,
                     password=DB_PASSWORD, database=DB_NAME)
        self.username = ""
        self.id = 0

    def set_username(self, username):
        self.username = username

    def send_message(self, current_user, message_id, message, now, room_id):
        self.db.add_to("Message", MessageID=message_id, UserID=current_user, Content=message, DateTime=now,
                       RoomID=room_id)

    def get_rooms(self, user_id):
        condition = f"UserID = '{user_id}' OR FriendID = '{user_id}'"
        results = self.db.get_all_where("Friends", condition, "RoomID", "FriendID", "UserName")
        return results

    def accept_action(self, request_id: int, user_id: str, friend_id: str):
        # Update the request status to accepted
        self.db.update_at("Users", condition=f"UserID = '{friend_id}'", IsAccept=1)
        self.db.update_at("Requests", condition=f"RequestID = {request_id}", IsAccept=1)

        # Fetch user details to get the user's name
        friend_result = self.db.get_one("Users", "UserID", friend_id)
        friend_name = ""
        if friend_result:
            friend_name = friend_result[2] if friend_result[2] else "Unknown"

        result = self.db.get_one("Users", "UserID", user_id)
        user_name = ""
        if user_name:
            user_name = result[2] if result[2] else "Unknown"

        # Add the user to the friends list
        self.db.add_to("Friends", RoomID=self.id, UserID=user_id, FriendID=friend_id, UserName=user_name,
                       FriendName=friend_name)
        self.id = + 1

    def decline_action(self, request_id: int, user_id: str, friend_id: str):
        self.db.delete_rows("Requests", condition=f"RequestID = {request_id}")
        self.db.delete_columns("Users", condition=f"UserID = '{friend_id}'")
        self.db.delete_columns("Users", condition=f"UserID = '{user_id}'")

    def send_request(self, current_user, search_value):
        # Check if a record with the specified UserID exists
        if self.has_record(table='Users', UserID=search_value):
            now = datetime.now()

            friend_condition = f"UserID = '{search_value}'"
            current_user_condition = f"UserID = '{current_user}'"

            # To Not Send the request again
            if self.has_record("Requests", UserID=current_user, FriendID=search_value):
                return False

            self.db.update_at("Users", condition=current_user_condition, FriendID=search_value)
            self.db.update_at("Users", condition=friend_condition, FriendID=current_user)

            self.db.add_to('Requests', RequestID=self.id, UserID=current_user, FriendID=search_value, IsAccept=0,
                           RequestDateTime=now.strftime("%Y-%m-%d %H:%M:%S"))
            self.id += 1
            return True
        return False

    def has_record(self, table, **kwargs):
        columns = kwargs.keys()

        # Fetch all records from the table
        results = self.db.get_all(table, *columns)

        if results:
            for record in results:
                # Create a dictionary from the record tuple
                record_dict = dict(zip(columns, record))

                # Check if all column-value pairs match
                if all(record_dict[col] == val for col, val in kwargs.items()):
                    return True

        return False

    def _check_existing(self, username):
        results = self.db.get_all('Users', 'UserID')
        if results:
            for record in results:
                if username in record:
                    return True
        return False

    def set_newuser(self, name, username, password):
        if self._check_existing(username):
            return False
        try:
            self.db.add_to('Users', UserName=name, UserID=username, Password=password, IsOnline=1, IsAccept=0)
        except Exception as e:
            print(f"Error adding new user: {e}")
        finally:
            if self._check_existing(username):
                return True
            return False

    def get_request(self, current_user) -> list[dict]:
        # Fetch the data
        results = self.db.get_all('Requests', 'RequestID', 'UserID', 'FriendID', 'IsAccept', 'RequestDateTime')
        name_result = self.db.get_inner_join('Requests', 'Users', 'UserID', 'UserID', 'UserName')

        if name_result is None:
            return []

        # Create a dictionary to map UserID to UserName
        user_names = {}
        for result in name_result:
            # Ensure the result has enough elements
            if len(result) >= 2 and result[0] is not None:
                user_names[result[0]] = result[1]

        request_list = []
        for result in results:
            # Ensure the result has enough elements
            if len(result) >= 5:
                request_dict = {
                    'RequestID': result[0],
                    'UserID': result[1],
                    'Name': user_names.get(result[1], 'Unknown'),  # Get the name from the dictionary
                    'FriendID': result[2],
                    'IsAccept': result[3],
                    'RequestDateTime': result[4]
                }
                if request_dict['FriendID'] == current_user and request_dict['IsAccept'] != 1:
                    request_list.append(request_dict)

        return request_list

    def get_messages(self, room_id: int) -> list:
        condition = f"RoomID = {room_id}"
        results = self.db.get_all_where('Message', condition)
        return results
