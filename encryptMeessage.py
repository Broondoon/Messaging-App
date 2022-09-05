#!/usr/bin/env python3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

#Reference: https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3

def main():
    
    message = input("Enter message to be encrypted: ")

    priv_Key = RSA.generate(2048)
    pub_Key = priv_Key.publickey()

    exported_privKey = priv_Key.exportKey(format='PEM')
    exported_pubKey = pub_Key.exportKey(format='PEM')

    message = str.encode(message)

    pubKeyRSA = RSA.importKey(exported_pubKey)
    pubKeyRSA = PKCS1_OAEP.new(pubKeyRSA)
    encrypted_text = pubKeyRSA.encrypt(message)

    print("Your encrypted text: ", encrypted_text)


    privKeyRSA = RSA.importKey(exported_privKey)
    privKeyRSA = PKCS1_OAEP.new(privKeyRSA)
    decrypted_text = privKeyRSA.decrypt(encrypted_text)

    decrypted_text = decrypted_text.decode()


    print("Your decrypted message is: ", decrypted_text)


if __name__ == "__main__":
    main()