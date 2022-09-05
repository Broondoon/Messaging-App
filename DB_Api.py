from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from DBSetup import Users, MsgHistory
import json
from flask_marshmallow import Marshmallow
import psycopg2
from flask_ngrok import run_with_ngrok

app = Flask(__name__)

secret = []
with open('config.txt', 'r') as file:
    for line in file:
        for word in line.split():
            secret.append(word)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + secret[0] + ':' + secret[1] + '@localhost:5432/SecureMessaging'
# need to hide credentials

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ma = Marshmallow(app)
run_with_ngrok(app)

class MsgSchema(ma.Schema):
    class Meta:
        fields = ('sender', 'recipient', 'msg')

class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')

msg_schema = MsgSchema()
msg_schema = MsgSchema(many=True)

user_schema = UserSchema()
user_schema = UserSchema(many=True)
# Schema helps return database queries in a readable manner

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']

    new_user = Users(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    return "Successfully registered a new user"
# adds a user to the database

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = db.session.query(Users).filter_by(username=username).first()
    if user is None:
        return "User does not exist."

    if user.password == password:
        return "Authenticated"

    else:
        return "Incorrect Password"
# login, ended up not being used as users are logged in client side

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    username = request.json['username']
    user = db.session.query(Users).filter_by(username=username).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
    return "User: " + username + " has been deleted"
# deletes a users account from the database


@app.route('/get_users', methods = ['GET'])
def get_users():
    users = db.session.query(Users).all()

    result = user_schema.dump(users)

    dict = {}
    for index in range(len(result)):
        for key in result[index]:
            username = result[index]["username"]
            password = result[index]["password"]
            dict[username] = password

    return dict
# returns all users in the database to the client

@app.route('/msg', methods=['POST'])
def msg():
    sender = request.json['sender']
    recipient = request.json['recipient']
    msg = request.json['msg']
   # time = request.json['time']

   # new_msg = MsgHistory(sender = sender, recipient = recipient, msg = msg, time = time)
    new_msg = MsgHistory(sender=sender, recipient=recipient, msg=msg)

    db.session.add(new_msg)
    db.session.commit()

    return "Message received"
# when a message is sent it is stored in the database

@app.route('/get_msg_sent', methods=['GET'])
def get_msg_sent():
    user = request.json["user"]
    msgs = db.session.query(MsgHistory).filter_by(sender = user).all()

    try:
        msgs[0]
    except:
        return "None"
    # there are no messages returned

    result = msg_schema.dump(msgs)

    return jsonify(result)
# queries for all messages sent by the user


@app.route('/get_msg_received', methods=['GET'])
def get_msg_received():
    user = request.json["user"]
    msgs = db.session.query(MsgHistory).filter_by(recipient = user).all()

    try:
        msgs[0]
    except:
        return "None"
    # there are no messages returned

    result = msg_schema.dump(msgs)

    return jsonify(result)
# queries for all messages received by the user

@app.route('/del_msgs', methods=['DELETE'])
def del_msgs():
    user = request.json["user"]
    msgs_sent = db.session.query(MsgHistory).filter_by(sender = user).all()

    for msg in msgs_sent:
        db.session.delete(msg)

    msgs_recv = db.session.query(MsgHistory).filter_by(recipient = user).all()

    for msg in msgs_recv:
        db.session.delete(msg)

    db.session.commit()

    return "Chat History Cleared"
# queries the database for all messages the user has sent/received and deletes them

if __name__ == '__main__':
    app.run()
