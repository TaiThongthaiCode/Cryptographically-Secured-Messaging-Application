import os, sys, getopt, time

import pyDHE

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

def listen_server_key():

    while True:
        status, msg = NETIF.receive_msg()

        if status:
            return msg 
    


def send_public_key():

    User = pyDHE.new()
    msg = str(User.getPublicKey())
    dst = SERVER_ADDR

    NETIF.send_msg(dst, msg.encode('utf-8'))

    return User

def main():

    User = send_public_key()
    serverkey = int(listen_server_key())
    
    SESSIONKEY = User.update(serverkey)

    print(SESSIONKEY)

if __name__ == "__main__":

    main()