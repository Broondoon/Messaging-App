# How To Use
To begin, the user will run the python program "UserInterface.py". This will begin a menu system which the user can navigate by entering keywords. The first thing a user must do is log in or create a new account. Then they'll have access to their message history, option to delete their account or their message history, and the ability to chat. To chat, the user must choose between being a host of the chatroom, or connecting to an existing one.

# Secure Messaging
#### The API
The API is a layer between the database and the application that the user interacts with. Whenever a user logs/registers/sends a message/views and deletes history an HTTP request is sent to the API containing the relevant information for the request. Each one of these actions is sent to their own route according to the action they perform. The API accesses the database and stores the relevant information, and responds appropriately in the form of a database query or a status message.  

#### Database: 
The database contains two tables. One table for the users, containing columns for the username of the user and the hashed password for this account, and one table for the message history, containing columns for the message sender, message recipient and the message itself (aids in non repudiation of the messages sent). The database can only be accessed through the API at certain routes. 

#### Encryption:
##### Password Encryption:
To keep passwords secure, we used sha-256 hashing. Whether logging in or creating a new account, the password must be encrypted. If creating a new account, the password that the user chooses must be encrypted, then stored in the database encrypted. When trying to log in, the password that the user attempts to log in with is encrypted and its hash is compared to the corresponding hash for that user within the database.

##### Message Encryption:
For messaging, we used RSA encryption. Once two users log in the chat, each will generate 2 keys, one will be the public key and the other is the private key. The public key is then shared between the two clients. Therefore, each client is encrypting their message with the recipients public key in order for it to be able decrypted. We send message through a json.dump string, so we decided this string should be encrypted on the senders side and decrypted on the recipients side. 

#### Message Sending:
##### Sockets:
Text and images are sent across a shared python socket between the two users. One user is designated a "Host" and the other a "Client". The Host creates the socket and binds it to port and IP address. Then it listens in for a connection, allowing only 1. The Client then can connect to the Host, and begin messaging. Information is sent across the socket via a stream of bytes objects.

##### Multi-Threaded Programming:
The program uses multi-threading programming in order to continuously and simultaneously wait for user input and wait for incoming messages. One thread, "Set()", handles receiving input from the user and sending the encrypted input across the Socket as a bytes object. If the user inputs one of two keywords, different functionalities like sending an image or quitting can occur. The other thread, "Get()", handles catching everything sent across the socket.

##### Text Support:
As text does not require a large amount of bytes, sending it across is relatively simple. Before any message is sent, a json package is sent across the socket, to inform the recipient of how to handle the received message. With text messages, a "txt" flag is sent, along with the contents of the message. The receiver

##### Image Support: 
Images are much larger, and so must be sent across the socket in a continuous stream of bytes. To inform the receiver that an image is incoming, a package with an "img" flag along with image name and file size is sent.

# Known Limitations
One particularly frustrating issue was transmitting images. A detailed explanation of the error found is in the comments of the chat_server and client files, but needless to say, a perfect solution was not found. Since the developer who made that section was using sockets for the first time, they had to do a band-aid fix. The amount of times a loop runs is hard-coded, and so only works with images greater than a certain size. If an image is too small, the program will infinitely wait for more bytes to arrive. More experience and education with sockets would be needed to solve this problem.