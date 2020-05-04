import json
import pyDHE
import session as s
import os, sys, getopt, time

from adapter import *
from os import walk
from base64 import b64decode
from base64 import b64encode
from netinterface import network_interface

#Path of the Server File
RELATIVE_SERVER_PATH = "/Users/Tai/Desktop/crypto_project/netsim/server/"

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
    print("Successfully created a secure channel")

    session = s.Session(SESSIONKEY)

    if not os.path.exists(RELATIVE_SERVER_PATH):
        server.mk_dir(RELATIVE_SERVER_PATH)


    print('Main loop started...')
    while True:
        skip_flag = False
        network_status, msg = server.listen()

        if network_status:
            print("Success: Message received")

            #NOTE: HEDAER IS IN JSON
            header, plaintext = session.parse_msg(msg)
            command = header["command"]
            nonce = header["nonce"]
            success = header["success"]

            #print("NONCE ", session.seq_num)
            
            if(command=="MKD"):

                abs_path = RELATIVE_SERVER_PATH + plaintext
                script_dir = os.path.abspath(abs_path)
                session.mk_dir(script_dir)


            elif(command=="RMD"):

                dir_path = RELATIVE_SERVER_PATH + plaintext
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        file_path = dir_path + "/" + filename
                        session.del_file(file_path)

                    session.del_directory(dir_path)
                else:
                    skip_flag = True
                    plaintext = "ERROR: Folder does not exist!"
                    plaintext = plaintext.encode('utf-8')
                    nonce = session.seq_num
                    encrypt_and_send(session, server, None, nonce, plaintext)

            elif(command=="GWD"):
                send_success(session, server)
                folder_title = session.getTitle(RELATIVE_SERVER_PATH)
                plaintext = folder_title.encode('utf-8')
                nonce = session.seq_num + 1
                encrypt_and_send(session, server, None, nonce, plaintext)

                status, msg = server.listen()
                header, plaintext = session.parse_msg(msg)
                skip_flag = True

            elif(command=="BWD"):
                listOfGlobals = globals()
                temp_path = session.back_folder(RELATIVE_SERVER_PATH)
                if("server" in temp_path):
                    listOfGlobals["RELATIVE_SERVER_PATH"] = temp_path
                else:
                    skip_flag = True
                    plaintext = "ERROR: Can't go past Server Folder!"
                    plaintext = plaintext.encode('utf-8')
                    nonce = session.seq_num
                    encrypt_and_send(session, server, None, nonce, plaintext)

            elif(command=="EWD"):
                listOfGlobals = globals()
                temp_path = RELATIVE_SERVER_PATH + plaintext + '/'
                if os.path.exists(temp_path):
                    listOfGlobals["RELATIVE_SERVER_PATH"] = temp_path
                else:
                    skip_flag = True
                    plaintext = "ERROR: Folder does not Exist!"
                    plaintext = plaintext.encode('utf-8')
                    nonce = session.seq_num
                    encrypt_and_send(session, server, None, nonce, plaintext)

            elif(command=="LST"):
                send_success(session, server)
                #Letting server know info about folder: how many files+folder
                path, dirs, files = next(os.walk(RELATIVE_SERVER_PATH))
                file_count = len(files) + len(dirs)
                folder_info = str(file_count)
                plaintext = folder_info.encode('utf-8')
                nonce = session.seq_num + 1
                encrypt_and_send(session, server, None, nonce, plaintext)

                status, msg = server.listen()

                for filename in os.listdir(RELATIVE_SERVER_PATH):
                    plaintext = filename.encode('utf-8')
                    nonce = session.seq_num + 1
                    encrypt_and_send(session, server, None, nonce, plaintext)
                    status, msg = server.listen()

                skip_flag = True

            elif(command=="UPL"):
                title = plaintext.partition("\n")[0]
                abs_path = RELATIVE_SERVER_PATH + title
                script_dir = os.path.abspath(abs_path)
                f = open(script_dir, 'a')
                f.write(plaintext.partition("\n")[2])
                f.close()

            elif(command=="UPD"):
                title = plaintext.partition("\n")[0]
                abs_path = RELATIVE_SERVER_PATH + title
                if os.path.exists(abs_path):
                    script_dir = os.path.abspath(abs_path)
                    session.del_file(script_dir)
                    f = open(script_dir, 'a')
                    f.write(plaintext.partition("\n")[2])
                    f.close()
                else:
                    skip_flag = True
                    plaintext = "ERROR: File does not Exist!"
                    plaintext = plaintext.encode('utf-8')
                    nonce = session.seq_num
                    encrypt_and_send(session, server, None, nonce, plaintext)

            elif(command=="DNL"):

                path = RELATIVE_SERVER_PATH + plaintext
                if os.path.exists(path):
                    send_success(session, server)
                    plaintext = session.upload_file_helper(path)
                    nonce = session.seq_num + 1

                    encrypt_and_send(session, server, None, nonce, plaintext)

                    status, msg = server.listen()
                    header, plaintext = session.parse_msg(msg)
                    skip_flag = True
                else:
                    skip_flag = True
                    plaintext = "ERROR: File does not Exist!"
                    plaintext = plaintext.encode('utf-8')
                    nonce = session.seq_num
                    encrypt_and_send(session, server, None, nonce, plaintext)

            elif(command=="RMF"):
                abs_path = RELATIVE_SERVER_PATH + plaintext
                script_dir = os.path.abspath(abs_path)
                if os.path.exists(script_dir):
                    session.del_file(script_dir)
                else:
                    skip_flag = True
                    plaintext = "ERROR: File does not exist!"
                    plaintext = plaintext.encode('utf-8')
                    nonce = session.seq_num
                    encrypt_and_send(session, server, None, nonce, plaintext)







            if(skip_flag == False):
                send_success(session, server)


def send_success(session, server):
    seq_num = session.seq_num

    response_header = session.create_header(None, OWN_ADDR, nonce=seq_num, success=True)
    plaintext = b"SUCCESS"
    ciphertext, tag = session.encrypt(response_header, plaintext)

    msg = session.create_msg(response_header, ciphertext, tag)
    server.send(msg, CLIENT_ADDR)

def encrypt_and_send(session, server, user_input, nonce, plaintext):
    header = session.create_header(user_input, OWN_ADDR, nonce)
    ciphertext, tag = session.encrypt(header, plaintext)
    msg = session.create_msg(header, ciphertext, tag)
    server.send(msg, CLIENT_ADDR)



if __name__ == "__main__":

    main()
