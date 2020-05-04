import json
import pyDHE
import session as s
import os, sys, getopt, time

from adapter import *
from os import walk
from base64 import b64encode
from base64 import b64decode
from netinterface import network_interface

NET_PATH = './network/'
SERVER_ADDR = 'A'
OWN_ADDR = 'B'
ADDR_SPACE = 'ABC'

#Address of the Client Path
CLIENT_FOLDER_PATH = "/Users/Tai/Desktop/crypto_project/netsim/client/"

NETIF = network_interface(NET_PATH, OWN_ADDR)

def main():
    client = Adapter(NET_PATH, OWN_ADDR)

    #Creating key with server via Diffie-Hellman Protocol
    User = client.send_public_key(SERVER_ADDR)
    status, msg = client.listen()
    serverkey = int(msg)

    SESSIONKEY = User.update(serverkey)

    session = s.Session(SESSIONKEY)

    if not os.path.exists(CLIENT_FOLDER_PATH):
        server.mk_dir(CLIENT_FOLDER_PATH)

    print("\n")
    print("Main loop started...")
    print(2*"\n")
    print("Welcome to Secure Server Protocol")
    print("\n")
    print("Enter 'help' for instructions")
    print(3*"\n")


    while True:
        skip_flag = False
        user_input = input("> ")

        #Help Screen
        if(user_input == 'help'):
            print("List of Commands:")
            print("MKD - Make folder on the Server")
            print("RMD - Remove a folder from the Server")
            print("GWD - Asking for name of current folder on Server")
            print("BWD - Go to previous folder on Server ")
            print("EWD - Enter a folder on Server")
            print("LST - List the contents of Folder on Server")
            print("UPL - Upload a File on the Server")
            print("DNL - Download a File on the Server")
            print("RMF - Remove a File on the Server")
            print("UPD - Update a File on the Server")
            skip_flag = True





        elif(user_input == "MKD"):
            print("What would you like to name the Folder?")
            new_folder_name = input('> ')

            plaintext = new_folder_name.encode('utf-8')
            nonce = session.seq_num + 1

        elif(user_input == "RMD"):
            print("What Folder would you like to Delete?")
            del_folder_name = input('> ')

            plaintext = del_folder_name.encode('utf-8')
            nonce = session.seq_num + 1

        elif(user_input == "GWD"):
            #SEND OVER COMMAND
            plaintext = user_input.encode('utf-8')
            nonce = session.seq_num + 1
            encrypt_and_send(session, client, user_input, nonce, plaintext)

            #LISTENS FOR SUCCESS FLAG
            status, msg = client.listen()

            #LISTENS FOR FOLDER NAME
            network_status, server_msg = client.listen()
            if network_status:
                header, plaintext = session.parse_msg(server_msg)

                print("CURRENT FOLDER: " + plaintext)
                #SEND SUCCESS FLAG
                send_success(session, client)
                skip_flag = True

        elif(user_input == "BWD"):
            #SEND OVER COMMAND
            plaintext = user_input.encode('utf-8')
            nonce = session.seq_num + 1

        elif(user_input == "EWD"):
            print("Which Folder would you like to ENTER?")
            enter_folder_name = input('> ')

            plaintext = enter_folder_name.encode('utf-8')
            nonce = session.seq_num + 1

        elif(user_input == "LST"):
            #SEND OVER COMMAND
            plaintext = user_input.encode('utf-8')
            nonce = session.seq_num + 1
            encrypt_and_send(session, client, user_input, nonce, plaintext)

            #LISTENS FOR SUCCESS FLAG
            status, msg = client.listen()
            #LISTENS FOR FOLDER INFO
            status2, info_msg = client.listen()
            print("LIST:")
            if status2:
                #NOTE: HEDAER IS IN JSON
                header, plaintext_num = session.parse_msg(info_msg)
                send_success(session, client)

                count = 0
                while(count < int(plaintext_num)):
                    status, msg = client.listen()
                    if status:
                        header, file_name = session.parse_msg(msg)
                        print(file_name)
                    count += 1
                    send_success(session, client)

            skip_flag = True

        elif(user_input == "UPL" or user_input == "UPD"):
            print("Which File from Client would you like to Upload/Update?")
            print("Please give the path relative from Client Folder")
            file_name = input('> ')

            path = CLIENT_FOLDER_PATH + file_name
            if os.path.exists(path):
                plaintext = session.upload_file_helper(path)
                nonce = session.seq_num + 1
            else:
                skip_flag = True
                print("ERROR: No such File in Client!")

        elif(user_input == "DNL"):
            print("Which File would you like to Download?")
            file_name = input('> ')

            plaintext = file_name.encode('utf-8')
            nonce = session.seq_num + 1

            encrypt_and_send(session, client, user_input, nonce, plaintext)

            #LISTENS FOR SUCCESS FLAG
            status, msg = client.listen()
            header, plaintext = session.parse_msg(msg)
            if(plaintext=="SUCESS"):
                #Listens for File
                status2, file = client.listen()
                if status2:
                    header, plaintext = session.parse_msg(file)
                    title = plaintext.partition("\n")[0]
                    abs_path = CLIENT_FOLDER_PATH + title
                    script_dir = os.path.abspath(abs_path)
                    f = open(script_dir, 'a')
                    f.write(plaintext.partition("\n")[2])
                    f.close()
                skip_flag = True
            else:
                skip_flag = True
                print(plaintext)

        elif(user_input == "RMF"):
            print("Which File would you like to Remove from Server?")
            file_name = input('> ')
            plaintext = file_name.encode('utf-8')
            nonce = session.seq_num + 1

        else:
            print("Input Not Defined. Please Type 'help' for commands")
            skip_flag = True



        if(skip_flag == False):
            encrypt_and_send(session, client, user_input, nonce, plaintext)
            status, msg = client.listen()

            #Decrypt from the server and increment counter
            #NOTE: HEADER IN JSON FORMAT
            header, plaintext = session.parse_msg(msg)

            #print(plaintext)
            #print("NONCE ", session.seq_num)


            #if input('Continue? (y/n): ') == 'n': break


def encrypt_and_send(session, client, user_input, nonce, plaintext):
    header = session.create_header(user_input, OWN_ADDR, nonce)
    ciphertext, tag = session.encrypt(header, plaintext)
    msg = session.create_msg(header, ciphertext, tag)
    client.send(msg, SERVER_ADDR)

def send_success(session, client):
    seq_num = session.seq_num

    response_header = session.create_header(None, OWN_ADDR, nonce=seq_num, success=True)
    plaintext = b"SUCCESS"
    ciphertext, tag = session.encrypt(response_header, plaintext)

    msg = session.create_msg(response_header, ciphertext, tag)
    client.send(msg, SERVER_ADDR)






if __name__ == "__main__":

    main()
