import os, sys, getopt, time

from base64 import b64decode

import json
import pyDHE

from adapter import *
import session as s

from netinterface import network_interface

RELATIVE_SERVER_PATH = "C:/Users/rchen/Documents/AIT Crypto/finalproject/CryptoProject-master/netsim/network/A/server/"
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

    if not os.path.exists(RELATIVE_SERVER_PATH):
        server.mk_dir(RELATIVE_SERVER_PATH)

    print('Main loop started...')
    while True:

        status, msg = server.listen()

        if status:
            server.send("Success", CLIENT_ADDR)
            print("Success: Message received")

            msg = json.loads(msg.decode("utf-8"))
            #print(type(msg), msg)

            #all of these are in bytes
            header = b64decode(msg['header'])
            ciphertext = b64decode(msg['ciphertext'])
            tag = b64decode(msg['tag'])

            #plaintext in bytes
            plaintext = session.decrypt(header, ciphertext, tag)
            plaintext = plaintext.decode("utf-8")
            header = json.loads(header.decode("utf-8"))
            src_add = header["from"]
            type = header["type"]
            command = header["command"]
            #print(plaintext)

            if(type=="File" and command=="Upload"):

                title = plaintext.partition("\n")[0]
                abs_path = RELATIVE_SERVER_PATH + title
                script_dir = os.path.abspath(abs_path)
                f = open(script_dir, 'a')
                f.write(plaintext.partition("\n")[2])
                f.close()


            elif(type=="File" and command=="Delete"):

                abs_path = RELATIVE_SERVER_PATH + plaintext
                script_dir = os.path.abspath(abs_path)

                server.del_file(script_dir)

            elif(type=="File" and command=="Update"):
                title = plaintext.partition("\n")[0]
                abs_path = RELATIVE_SERVER_PATH + title
                script_dir = os.path.abspath(abs_path)

                server.del_file(script_dir)

                f = open(script_dir, 'a')
                f.write(plaintext.partition("\n")[2])
                f.close()

            elif(type=="File" and command=="Download"):
                #RELATIVE_SERVER_PATH = "C:/Users/rchen/Documents/AIT Crypto/finalproject/CryptoProject-master/netsim/server/"
                abs_path = RELATIVE_SERVER_PATH + plaintext


                #encryption
                plaintext = server.upload_file_helper(abs_path)
                header = server.create_header(type, command)
                ciphertext, tag = session.encrypt(header, plaintext)

                msg = server.create_msg(header, ciphertext, tag)
                server.send(msg, CLIENT_ADDR)
                status = server.listen()
                if status:
                    print("Message successfully sent")
                else:
                    print("Error: message could not send. Look up stackoverflow for more info")

            elif(type=="Folder" and command=="Push"):
                num_files = plaintext.partition("\n")[0]
                file_name = plaintext.partition("\n")[2]

                new_dir_path = RELATIVE_SERVER_PATH + file_name

                server.mk_dir(new_dir_path)

                count = 0
                while(count != int(num_files)):
                    #Keep listening and creating files

                    status, msg = server.listen()
                    if status:
                        server.send("Success", CLIENT_ADDR)
                        print("Success: Message received")

                        msg = json.loads(msg.decode("utf-8"))
                        #print(type(msg), msg)

                        #all of these are in bytes
                        header = b64decode(msg['header'])
                        ciphertext = b64decode(msg['ciphertext'])
                        tag = b64decode(msg['tag'])

                        #plaintext in bytes
                        plaintext = session.decrypt(header, ciphertext, tag)
                        plaintext = plaintext.decode("utf-8")
                        header = json.loads(header.decode("utf-8"))
                        src_add = header["from"]
                        type = header["type"]
                        command = header["command"]

                        title = plaintext.partition("\n")[0]
                        abs_path = new_dir_path + "/" + title
                        script_dir = os.path.abspath(abs_path)
                        f = open(script_dir, 'a')
                        f.write(plaintext.partition("\n")[2])
                        f.close()
                        count += 1

            elif(type=="Folder" and command=="Pull"):

                abs_path = RELATIVE_SERVER_PATH + plaintext

                if(abs_path[-1] == "/"):
                    abs_path = abs_path[:-1]

                #Letting server know info about folder: how many files, name of folder
                path, dirs, files = next(os.walk(abs_path))
                file_count = len(files)
                folder_title = server.getTitle(abs_path)

                folder_info = str(file_count) + "\n" + folder_title

                plaintext = folder_info.encode('utf-8')
                header = server.create_header(type, command)
                ciphertext, tag = session.encrypt(header, plaintext)
                msg = server.create_msg(header, ciphertext, tag)
                server.send(msg, CLIENT_ADDR)

                status = server.listen()
                if status:
                    print("Folder Info")
                else:
                    print("Error: message could not send. Look up stackoverflow for more info")

                #For each file in directory, upload
                for filename in os.listdir(abs_path):
                    #filename is just the name of the file
                    file_path = abs_path + "/" +filename
                    plaintext = server.upload_file_helper(file_path)

                    header = server.create_header(type, command)
                    ciphertext, tag = session.encrypt(header, plaintext)
                    msg = server.create_msg(header, ciphertext, tag)
                    server.send(msg, CLIENT_ADDR)

            elif(type=="Folder" and command=="Update"):
                num_files = plaintext.partition("\n")[0]
                file_name = plaintext.partition("\n")[2]

                new_dir_path = RELATIVE_SERVER_PATH + file_name

                for filename in os.listdir(new_dir_path):
                    #filename is just the name of the file
                    file_path = new_dir_path + "/" +filename
                    server.del_file(file_path)


                server.del_directory(new_dir_path)
                server.mk_dir(new_dir_path)

                count = 0
                while(count != int(num_files)):
                    #Keep listening and creating files

                    status, msg = server.listen()
                    if status:
                        server.send("Success", CLIENT_ADDR)
                        print("Success: Message received")

                        msg = json.loads(msg.decode("utf-8"))
                        #print(type(msg), msg)

                        #all of these are in bytes
                        header = b64decode(msg['header'])
                        ciphertext = b64decode(msg['ciphertext'])
                        tag = b64decode(msg['tag'])

                        #plaintext in bytes
                        plaintext = session.decrypt(header, ciphertext, tag)
                        plaintext = plaintext.decode("utf-8")
                        header = json.loads(header.decode("utf-8"))
                        src_add = header["from"]
                        type = header["type"]
                        command = header["command"]

                        title = plaintext.partition("\n")[0]
                        abs_path = new_dir_path + "/" + title
                        script_dir = os.path.abspath(abs_path)
                        f = open(script_dir, 'a')
                        f.write(plaintext.partition("\n")[2])
                        f.close()
                        count += 1

            elif(type=="Folder" and command=="Delete"):

                new_dir_path = RELATIVE_SERVER_PATH + plaintext

                for filename in os.listdir(new_dir_path):
                    #filename is just the name of the file
                    file_path = new_dir_path + "/" +filename
                    server.del_file(file_path)

                server.del_directory(new_dir_path)

            elif(type=="Folder" and command=="Make"):

                abs_path = RELATIVE_SERVER_PATH + plaintext
                script_dir = os.path.abspath(abs_path)

                server.mk_dir(script_dir)









if __name__ == "__main__":

    main()
