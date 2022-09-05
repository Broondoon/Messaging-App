import hashlib
import requests
import ast
import json
import chat_server
import client

username = None

route = "http://5b75-2604-3d08-267e-d620-f11e-969a-79bd-37f.ngrok.io"
header = {'Content-Type': 'application/json'}

def encryptPassword(password, status):

    encodedPassword = password.encode() #Convert password to bytes

    hashOb = hashlib.sha256(encodedPassword) #Create hash object

    finalPassword = hashOb.hexdigest() #Convert to hexadecimal format

    # The commented code below should be uncommented
    # Once the UserInterface is merged with the DB

    if(status == "new"):

        data = {"username": username, "password": finalPassword}
        url = route + "/register"
        requests.post(url, data = json.dumps(data), headers = header)
        return finalPassword
        #Store in DB
    elif(status == "existing"):
        return finalPassword
        #Check in DB

class UserInterface:

    def __init__(self, database):
        self.database = database
        self.active_account = ""

    def request(self):
        action = input("Enter L for login and C to create a new account:")
        if action == "L":
            return 1
        elif action == "C":
            return 2
        else:
            return 3

    def login(self):
        username = input("Enter Username:")
        password = input("Enter Password:")
        try:
            x = self.database[username]
        except KeyError:
            print("Invalid Username")
            return False

        password_enc = encryptPassword(password, "existing")
        if x == password_enc:
            #encryptPassword(password, "existing")
            self.active_account = username
            return True
        else:
            return False

    def new_account(self, username, password):
        password_enc = encryptPassword(password, "new")
        if username not in self.database.keys():
            self.database[username] = password_enc
        else:
            print("This user already exists")

    def delete_account(self):
        print(self.database)
        del self.database[self.active_account]


if __name__ == '__main__':
    url = route + "/get_users"
    # this url will change, i am sorry
    response = requests.get(url)
    db = response.content
    db = db.decode('utf-8')
    db = ast.literal_eval(db)
    # converting bytes into string into dict

    database = db
    user = UserInterface(database)

    while True:
        action = user.request()
        if action == 1:
            access = user.login()
            break
        elif action == 2:
            username = input("Enter new username:")
            password = input("Enter new password:")
            # can add from here

            user.new_account(username, password)
        else:
            print("Invalid Input")

    if access:

        while True:
            next_action = input("press D to delete your account, L for message history, DM to delete message history, H to host, C to connect to a host.")
            if next_action == "D":
                user_to_delete = user.active_account
                user.delete_account()

                data = {"username": user_to_delete}
                url = route + "/delete_user"
                requests.delete(url, data = json.dumps(data), headers = header)
                print("account deleted")
                break
            elif next_action == "H": #host
                print("Starting up communications.")
                print("Please wait for other user to connect...")
                chat_server.start_communication(user.active_account)
                break
            elif next_action == "C": #client
                print("Starting up communications.")
                client.start_communication(user.active_account)
                break
            elif next_action == "L":
                user_to_query = user.active_account
                url = route + "/get_msg_sent"
                data = {"user": user_to_query}
                response = requests.get(url, data = json.dumps(data), headers = header)
                # Query the database for the messages sent by this user
                if response.content.decode('utf-8') == "None":
                    print("User has not sent any messages")
                    # when they havent sent any messages
                else:
                    print("\nMessages sent")
                    print("=============")
                    dict = ast.literal_eval(response.content.decode('utf-8'))
                    # print(dict)
                    for index in range(len(dict)):
                        print("Sent to: " + dict[index]["recipient"])
                        print("Message: " + dict[index]["msg"] + "\n")
                    # loop through each message in the query and print who it was sent to and what it says

                url = route + "/get_msg_received"
                response = requests.get(url, data = json.dumps(data), headers = header)

                if response.content.decode('utf-8') == "None":
                    print("User has not received any messages")
                else:
                    print("\nMessages received")
                    print("=============")
                    dict = ast.literal_eval(response.content.decode('utf-8'))
                    # print(dict)
                    for index in range(len(dict)):
                        print("Sent from: " + dict[index]["sender"])
                        print("Message: " + dict[index]["msg"] + "\n")
                # repeating the process for messages received
            elif next_action == "DM":
                user_to_query = user.active_account
                url = route + "/del_msgs"
                data = {"user": user_to_query}
                response = requests.delete(url, data = json.dumps(data), headers = header)
                print(response.content.decode('utf-8'))
                # sent a delete request to delete the message history of a user in the database

            else:
                print("wrong input")
