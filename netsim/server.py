import os, sys, getopt, time

import pyDHE

from netinterface import network_interface

# import network
# import netinterface 
# import receiver 
# import sender 

NET_PATH = './network/'
OWN_ADDR = 'A'
CLIENT_ADDR = 'B'
ADDR_SPACE = 'ABC'

NETIF = network_interface(NET_PATH, OWN_ADDR)

def listen_server_key():

    while True:
        status, msg = NETIF.receive_msg()

        if status:
            return msg 
        

def send_public_key():

    Server = pyDHE.new()
    msg = str(Server.getPublicKey())
    dst = CLIENT_ADDR

    NETIF.send_msg(dst, msg.encode('utf-8'))

    return Server

def main():

    clientkey = int(listen_server_key())
    Server = send_public_key()
    
    SESSIONKEY = Server.update(clientkey)

    print(SESSIONKEY)

if __name__ == "__main__":

    main()