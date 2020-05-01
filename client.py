import os, sys, getopt, time

from base64 import b64encode
import json
import pyDHE
import session as s
from adapter import *

from netinterface import network_interface

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

    print('Main loop started...')
    while True:


        # ========== TODO MAKE THIS LOOK NICE ===============
        print("Working with File or Folder?")
        type = input('> ')
        print("Upload, Download, Update, or Delete?")
        command = input('> ')
        # name = input('Name of thing')
        print("Content of File")
        plaintext = input('> ')
        plaintext = plaintext.encode('utf-8')

        header = client.create_header(type, command)

        ciphertext, tag = session.encrypt(header, plaintext)

        msg = client.create_msg(header, ciphertext, tag)

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
