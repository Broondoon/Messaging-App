import socket
import threading
import requests
import json
import glob  # module for searching directory
import sys  # module for checking sizeof thing
import select  # module for emptying the socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random

# Inspiration and the foundation of this code was created with the help of "Nivedh" and "J. Blackadar" on 
# StackOverflow.com. Please visit "https://stackoverflow.com/questions/51989384/create-messaging-system-in-python-using-socket-programming" for the original code.

'''The functions and their uses:
"socket.socket()" - Creates and returns a socket object.
"socket_obj.recv(num)" - Receives data from a socket object, num is the maximum amount of 
    data that can be received at one time. num should be a somewhat low power of 2.
    Returns a "bytes object"
        Python manual: "Bytes objects are immutable sequences of single bytes. Since many major binary protocols are based on the ASCII text encoding, bytes objects offer several methods that are only valid when working with ASCII compatible data and are closely related to string objects in a variety of other ways."
        Source: https://docs.python.org/3/library/stdtypes.html#bytes-objects
"input("msg")" - Sends a message, waits for keyboard input, returns that input 
    as a string.
"string.encode(type)" - Convert any unicode strings into any encodings supported
    by Python, which you specify with 'type'. In this program, we encode it with
    ASCII. This returns a bytes object.
"bytes_obj.decode(type)" - Turns a bytes object back into a string, using the
    decoding method 'type'. In this program, that'll be ASCII.
'''

# These setup the database interaction
header = {'Content-Type': 'application/json'}
route = "http://644e-2604-3d08-267e-d620-f11e-969a-79bd-37f.ngrok.io/"

def generateKeys():
    generator = Random.new().read
    priv_Key = RSA.generate(2048, generator)
    pub_Key = priv_Key.publickey()

    exported_privKey = priv_Key.exportKey(format='PEM')
    exported_pubKey = pub_Key.exportKey(format='PEM') #To send to server

    # pubKeyRSA = RSA.importKey(exported_pubKey)
    # pubKeyRSA = PKCS1_OAEP.new(pubKeyRSA)

    privKeyRSA = RSA.importKey(exported_privKey)
    privKeyRSA = PKCS1_OAEP.new(privKeyRSA) #To decrypt

    return exported_pubKey, privKeyRSA

def importNewKey(key):

    pubKeyRSA = RSA.importKey(key)
    pubKeyRSA = PKCS1_OAEP.new(pubKeyRSA)

    return pubKeyRSA

# Credit for this function: https://stackoverflow.com/questions/34252273/what-is-the-difference-between-socket-send-and-socket-sendall
def empty_socket(sock):
    """remove the data present on the socket"""
    input = [sock]
    while 1:
        inputready, o, e = select.select(input, [], [], 0.0)
        if len(inputready) == 0: break
        for s in inputready: s.recv(1)


# Thread function that recieves data cross the socket and displays it to the user
def get(s, privKey):
    while True:
        # Wait for a data package to be sent to us
        recieved_data = s.recv(1024)
        decryptedData = privKey.decrypt(recieved_data)  # Decrypt the json string
        # Unpackage that data (which was a bunch of bytes) into something we can actually use
        recieved_data = json.loads(decryptedData.decode())

        # Grab the flag from the data to inform us of how to handle the incoming data
        flag = recieved_data.get("flag")  # got_back.decode('ascii')

        # Determine what to do, depending if it's a txt flag or an img flag or otherwise
        if flag == "txt":
            # No need to wait for further information, when it's text, the text data is sent in the original package
            print("\nReceived: ", recieved_data.get("text_data"))
            print("\nEnter: ")
        elif flag == "img":
            # Grab the name of the image that will be sent, and create a new name for the incoming image
            img_name = "recv_" + recieved_data.get("image_name")

            # Notify the users they recieved an image
            print("\n\nYou've recieved an image!", img_name)
            print("\nEnter: ")

            # Create a file using the newly created image name
            file = open(img_name, "wb")

            # Begin the process of recieving the image - part of the original package gave a 'size' of the image.
            # We repeatedly ask for more data, only stopping when we've recieved enough data to fill the entire image.
            # This uses a counter variable that increases every loop iteration.
            bytes_done = 0
            size_of_image = recieved_data.get("image_size")
            while bytes_done < (size_of_image * 7):
                image_chunk = s.recv(2048)
                file.write(image_chunk)
                bytes_done += 2048
            file.close()
            # Bit of a weird thing happening with the loop condition... sys.getsizeof() returns a byte value that
            # does not match up with the number of bytes sent across the socket - I think this is because .getsizeof()
            # returns the byte size as well as garbage collector overhead (learned this from https://stackoverflow.com/questions/17574076/what-is-the-difference-between-len-and-sys-getsizeof-methods-in-python)
            # So I have to adjust, and the magic number that made it work was 7. So that's why there's a *7 in there.

            # Now there was another bug I just couldn't figure out due to my lack of experience with sockets and .recv().
            # No matter what I would do, there would always be a leftover opened recv(), which would grab the next input (didn't want that)!
            # So the band-aid solution was to just empty the socket of all awaiting recv() functions.
            empty_socket(s)
        else:
            # Something weird happened, likely flag was not sent.
            print("\nSomething went wrong.")


# Thread function that takes data provided by the user and sends it across the socket.
def set_(s, serverPubKey, self_name, partner_name):
    while True:
        # Grab text input from the user
        i = input("\nEnter: ")

        # Depending on the input, either repeat keywords, ask for images to send, or just send the input across the socket
        if i == "h":
            # Repeat the keywords message
            print("Type \"img\" to send an image, \"q\" to quit.")
            print("Type \"h\" to see this message again.")
        elif i == "img":
            print("So you'd like to send some images, eh?")

            # Grab list of all .png and .jpg files - in the current directory
            all_images = glob.glob("*.png") + glob.glob("*.jpg")

            # Iterate through that list, asking whether to send each image
            for img in all_images:

                # Ask to send image
                rep = input("Would you like to send \"" + img + "\"? [y/n]")

                # If they say yes:
                if rep == "y":
                    # Open the file we found that the user said they'd like to send
                    file = open(img, "rb")

                    # Send a preliminary package across the socket, so the reciever knows how to handle the image
                    pkg = json.dumps({"flag": "img", "image_name": img, "image_size": sys.getsizeof(file)})
                    encryptedpkg = serverPubKey.encrypt(pkg.encode()) #Encrypt image package
                    s.send(encryptedpkg)

                    # Read bytes from the image, sending them across the socket, and loop until we can't get any more data from the image
                    image_data = file.read(2048)
                    while image_data:
                        s.send(image_data)
                        image_data = file.read(2048)
                    file.close()

        elif i == "q":
            s.close()
            break
        else:
			# Now you can use "self_name" and "partner_name" here
            package = json.dumps({"flag": "txt", "text_data": i})
            encryptedPack = serverPubKey.encrypt(package.encode())  #Encrypt json
            s.send(encryptedPack)  #Send the encryped json string
            url = route + "/msg"
            data = {"sender": self_name, "recipient": partner_name, "msg": i}
            requests.post(url, data = json.dumps(data), headers = header)

# Function to create the socket, create keys and start the two threads which deal with communication.
def start_communication(user_name):
	# Create the socket
	s = socket.socket()
	host = socket.gethostname()
	port = 9981
	s.connect((host, port))

	# IDENTIFY YOURSELF and your friend
	partner_name = s.recv(1024).decode()
	s.send(user_name.encode())

	pubKey, privKey = generateKeys()

	s.send(pubKey) #Send client key to server

	serverPubKey = s.recv(2048) #Recieve the server key

	serverPubKey = importNewKey(serverPubKey) #Need to import the key from the server

	# Send out a preliminary message, to inform the user of some keywords they can use
	print("Type \"img\" to send an image, \"q\" to quit.")
	print("Type \"h\" to see this message again.")

	try:
		# Create and start the thread that recieves data across the socket
		t1 = threading.Thread(target=get, args=(s,privKey))
		t1.start()

		# Create and start the thread that sends data across the socket
		t2 = threading.Thread(target=set_, args=(s,serverPubKey, user_name, partner_name))#, user_name, partner_name))
		t2.start()
	except Exception:
		sys.exit()

# This is here so this all doesn't run when the file is imported
def main():
	pass
	#start_communication("Alice")

#if __name__ == '__main__':
#	main()
