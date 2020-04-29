import os, sys, getopt, time

from base64 import b64decode

import json
import pyDHE

from adapter import *
import session as s 

from netinterface import network_interface

# import network
# import netinterface 
# import receiver 
# import sender 

NET_PATH = './network/'
OWN_ADDR = 'A'
CLIENT_ADDR = 'B'
ADDR_SPACE = 'ABC'



def main():

    server = Adapter(NET_PATH, OWN_ADDR)

    status, msg = server.listen()
    clientkey = int(msg)
    Server = server.send_public_key(CLIENT_ADDR)
    SESSIONKEY = Server.update(clientkey)
    print("Sucessfully created a secure channel")

    session = s.Session(SESSIONKEY)

    print('Main loop started...')
    while True:
    
        status, msg = server.listen()
        
        if status:
            server.send("Success", CLIENT_ADDR)
            print("Success: Message received")

            msg = json.loads(msg.decode("utf-8"))
            print(type(msg), msg)

            #all of these are in bytes
            header = b64decode(msg['header'])
            ciphertext = b64decode(msg['ciphertext'])
            tag = b64decode(msg['tag'])

            #plaintext in bytes
            plaintext= session.decrypt(header, ciphertext, tag)

            print(header, plaintext)

if __name__ == "__main__":

    main()