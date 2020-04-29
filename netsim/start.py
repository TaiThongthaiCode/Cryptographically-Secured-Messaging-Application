import os, sys, getopt, time

from base64 import b64encode
import json
import pyDHE
import session as s
from adapter import *

from netinterface import network_interface

# import network
# import netinterface 
# import receiver 
# import sender 

NET_PATH = './network/'
SERVER_ADDR = 'A'
OWN_ADDR = 'B'
ADDR_SPACE = 'ABC'

NETIF = network_interface(NET_PATH, OWN_ADDR)

def main():

    client = Adapter(NET_PATH, OWN_ADDR)

    #Fix this
    User = client.send_public_key(SERVER_ADDR)
    status, msg = client.listen()
    serverkey = int(msg)
    
    SESSIONKEY = User.update(serverkey)

    session = s.Session(SESSIONKEY)

    # json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
    # json_v = [ b64encode(x).decode('utf-8') for x in cipher.nonce, header, ciphertext, tag ]
    # result = json.dumps(dict(zip(json_k, json_v)))

    print('Main loop started...')
    while True:


        # ========== TODO MAKE THIS LOOK NICE ===============
        msg = {}
        header = {}
        typ = input('Working with file or folder? ')
        command = input('Upload, download, update, or delete? ')
        # name = input('Name of thing')
        plaintext = input('Content of file') 
        plaintext = plaintext.encode('utf-8')

        header["from"] = OWN_ADDR
        header["type"] = typ
        header["command"] = command
        header = json.dumps(header).encode('utf-8')
        ciphertext, tag = session.encrypt(header, plaintext)

        msg["header"] = b64encode(header).decode('utf-8')
        msg["ciphertext"] = b64encode(ciphertext).decode('utf-8')
        msg["tag"] = b64encode(tag).decode('utf-8')

        msg = json.dumps(msg)
        print(msg)
        # ======================================================

        client.send(msg, SERVER_ADDR)
        status = client.listen()
        if status:
            print("Message successfully sent")
        else:
            print("Error: message could not send. Look up stackoverflow for more info")
        

        if input('Continue? (y/n): ') == 'n': break


if __name__ == "__main__":

    main()