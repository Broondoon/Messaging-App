import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

secret = []
with open('config.txt', 'r') as file:
    for line in file:
        for word in line.split():
            secret.append(word)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + secret[0] + ':' + secret[1] + '@localhost:5432/SecureMessaging'
# hiding credentials

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(50), primary_key = True)
    password = db.Column(db.String(100), nullable = False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
    # creates the users table with username and password columns

class MsgHistory(db.Model):
    '''Stores sender ID, Recipient ID, Encrypted Message and a Timestamp (could add image)'''
    __tablename__ = 'msghistory'

    msg_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    sender = db.Column(db.String(50))
    recipient = db.Column(db.String(50), nullable = False)
    msg = db.Column(db.String(50), nullable = False)

    def __init__ (self, sender, recipient, msg):
        self.sender = sender
        self.recipient = recipient
        self.msg = msg
    # creates the MsgHistory table and all the revelant columns


db.create_all()
db.session.commit()
print("Tables created")



if __name__ == '__main__':
    main()