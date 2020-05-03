import os, sys, getopt, time

from base64 import b64encode
from base64 import b64decode
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
        typee = input('> ')
        if(typee=="File"):
            print("Upload, Download, Update, or Delete")
            command = input('> ')

        elif(typee=="Folder"):
            print("Push, Pull, Update, Make, or Delete?")
            command = input('> ')

        if(typee=="File" and command=="Upload"):
            #Tested and working
            print("Please give the file source")
            src = input('> ')
            plaintext = client.upload_file_helper(src)
            nonce=session.seq_num + 1
            send_to_server(session, client, typee, command, plaintext, nonce=nonce)

        elif(typee=="File" and command=="Delete"):
            #Tested and Working
            print("Please give the relative directory and file name from server")
            rel_dir = input('> ')

            plaintext = rel_dir.encode('utf-8')
            send_to_server(session, client, typee, command, plaintext)

        elif(typee=="File" and command=="Update"):
            #Tested and Working
            print("Please give the file source")
            src = input('> ')
            plaintext = client.upload_file_helper(src)

            send_to_server(session, client, typee, command, plaintext)

        elif(typee=="File" and command=="Download"):
            print("Please give the relative directory and file name from server")
            rel_dir = input('> ')

            print("Please give the location of where you want this saved")
            save_dir = input('> ')

            plaintext = rel_dir.encode('utf-8')
            send_to_server(session, client, typee, command, plaintext)

            #Listening for Server Response
            status, msg = client.listen()
            if status:
                client.send("Success", SERVER_ADDR)
                print("Success: Message received")

                msg = json.loads(msg.decode("utf-8"))

                #all of these are in bytes
                header = b64decode(msg['header'])
                ciphertext = b64decode(msg['ciphertext'])
                tag = b64decode(msg['tag'])

                #plaintext in bytes
                plaintext = session.decrypt(header, ciphertext, tag)
                plaintext = plaintext.decode("utf-8")
                header = json.loads(header.decode("utf-8"))
                src_add = header["from"]
                typee = header["type"]
                command = header["command"]

                title = plaintext.partition("\n")[0]
                abs_path = save_dir + title
                script_dir = os.path.abspath(abs_path)
                f = open(script_dir, 'a')
                f.write(plaintext.partition("\n")[2])
                f.close()

        elif(typee=="Folder" and command=="Push"):
            print("Please give the folder source")
            src = input('> ')

            if(src[-1] == "/"):
                src = src[:-1]

            #Letting server know info about folder: how many files, name of folder
            path, dirs, files = next(os.walk(src))
            file_count = len(files)
            folder_title = client.getTitle(src)

            folder_info = str(file_count) + "\n" + folder_title

            plaintext = folder_info.encode('utf-8')
            header = client.create_header(typee, command)
            ciphertext, tag = session.encrypt(header, plaintext)
            msg = client.create_msg(header, ciphertext, tag)
            client.send(msg, SERVER_ADDR)
            status = client.listen()
            if status:
                print("Folder Info")
            else:
                print("Error: message could not send. Look up stackoverflow for more info")

            #For each file in directory, upload
            for filename in os.listdir(src):
                #filename is just the name of the file
                file_path = src + "/" +filename
                plaintext = client.upload_file_helper(file_path)

                header = client.create_header(typee, command)
                ciphertext, tag = session.encrypt(header, plaintext)
                msg = client.create_msg(header, ciphertext, tag)
                client.send(msg, SERVER_ADDR)

        elif(typee=="Folder" and command=="Pull"):
            print("Please give the relative directory from server")
            rel_dir = input('> ')

            print("Please give the location of where you want this saved")
            save_dir = input('> ')

            #Send Request to Server
            plaintext = rel_dir.encode('utf-8')
            header = client.create_header(typee, command)
            ciphertext, tag = session.encrypt(header, plaintext)
            msg = client.create_msg(header, ciphertext, tag)
            client.send(msg, SERVER_ADDR)
            status = client.listen()
            if status:
                print("Message successfully sent")
            else:
                print("Error: message could not send. Look up stackoverflow for more info")

            status, msg = client.listen()
            if status:
                client.send("Success", SERVER_ADDR)
                print("Success: Message received")

                msg = json.loads(msg.decode("utf-8"))

                #all of these are in bytes
                header = b64decode(msg['header'])
                ciphertext = b64decode(msg['ciphertext'])
                tag = b64decode(msg['tag'])

                #plaintext in bytes
                plaintext = session.decrypt(header, ciphertext, tag)
                plaintext = plaintext.decode("utf-8")
                header = json.loads(header.decode("utf-8"))
                src_add = header["from"]
                typee = header["type"]
                command = header["command"]

                num_files = plaintext.partition("\n")[0]
                file_name = plaintext.partition("\n")[2]

                new_dir_path = save_dir + file_name

                client.mk_dir(new_dir_path)

                count = 0
                while(count < int(num_files)):
                    status, msg = client.listen()
                    if status:
                        msg = json.loads(msg.decode("utf-8"))

                        #all of these are in bytes
                        header = b64decode(msg['header'])
                        ciphertext = b64decode(msg['ciphertext'])
                        tag = b64decode(msg['tag'])

                        #plaintext in bytes
                        plaintext = session.decrypt(header, ciphertext, tag)
                        plaintext = plaintext.decode("utf-8")
                        header = json.loads(header.decode("utf-8"))
                        src_add = header["from"]
                        typee = header["type"]
                        command = header["command"]

                        title = plaintext.partition("\n")[0]
                        abs_path = new_dir_path + "/" + title
                        script_dir = os.path.abspath(abs_path)
                        f = open(script_dir, 'a')
                        f.write(plaintext.partition("\n")[2])
                        f.close()
                        count += 1

        elif(typee=="Folder" and command=="Update"):
            print("Please give the folder source")
            src = input('> ')

            if(src[-1] == "/"):
                src = src[:-1]

            #Letting server know info about folder: how many files, name of folder
            path, dirs, files = next(os.walk(src))
            file_count = len(files)
            folder_title = client.getTitle(src)

            folder_info = str(file_count) + "\n" + folder_title

            plaintext = folder_info.encode('utf-8')
            header = client.create_header(typee, command)
            ciphertext, tag = session.encrypt(header, plaintext)
            msg = client.create_msg(header, ciphertext, tag)
            client.send(msg, SERVER_ADDR)
            status = client.listen()
            if status:
                print("Folder Info")
            else:
                print("Error: message could not send. Look up stackoverflow for more info")

            #For each file in directory, upload
            for filename in os.listdir(src):
                #filename is just the name of the file
                file_path = src + "/" +filename
                plaintext = client.upload_file_helper(file_path)

                header = client.create_header(typee, command)
                ciphertext, tag = session.encrypt(header, plaintext)
                msg = client.create_msg(header, ciphertext, tag)
                client.send(msg, SERVER_ADDR)

        elif(typee=="Folder" and command=="Delete"):
            print("Please give the relative directory and file name from server")
            rel_dir = input('> ')
            plaintext = rel_dir.encode('utf-8')

            header = client.create_header(typee, command)
            ciphertext, tag = session.encrypt(header, plaintext)
            msg = client.create_msg(header, ciphertext, tag)
            client.send(msg, SERVER_ADDR)
            status = client.listen()
            if status:
                print("Message successfully sent")
            else:
                print("Error: message could not send. Look up stackoverflow for more info")

        elif(typee=="Folder" and command=="Make"):
            print("Please name the directory")
            name = input('> ')
            plaintext = name.encode('utf-8')

            header = client.create_header(typee, command)
            ciphertext, tag = session.encrypt(header, plaintext)
            msg = client.create_msg(header, ciphertext, tag)
            client.send(msg, SERVER_ADDR)


        if input('Continue? (y/n): ') == 'n': break

def parse(msg):
    header = b64decode(msg['header'])
    ciphertext = b64decode(msg['ciphertext'])
    tag = b64decode(msg['tag'])

    #plaintext in bytes
    plaintext = session.decrypt(header, ciphertext, tag)
    plaintext = plaintext.decode("utf-8")
    header = json.loads(header.decode("utf-8"))
    src_add = header["from"]
    typee = header["type"]
    command = header["command"]

    return plaintext


#CURRENTLY ONLY RELEVENT TO 3/4 (DOWNLOAD DOESNT WORK WITH THIS) of file commands
def send_to_server(session, client, typee, command, plaintext, nonce, success=None):
    """
    Helper Function to send message to server
    """
    header = client.create_header(typee, command, nonce, success)
    ciphertext, tag = session.encrypt(header, plaintext)
    msg = client.create_msg(header, ciphertext, tag)
    client.send(msg, SERVER_ADDR)
    status, msg = client.listen()

    #DECRYPT AND INCREMENT
    msg = json.loads(msg.decode("utf-8"))

    #all of these are in bytes
    header = b64decode(msg['header'])
    ciphertext = b64decode(msg['ciphertext'])
    tag = b64decode(msg['tag'])

    #plaintext in bytes DECRYPTION OF MESSAGE
    plaintext = session.decrypt(header, ciphertext, tag)
    plaintext = plaintext.decode("utf-8")
    header = json.loads(header.decode("utf-8"))
    src_add = header["from"]
    typee = header["type"]
    command = header["command"]
    nonce = header["nonce"]
    success = header["success"]

    print("IN CLIENT.PY/FUNC:SEND_TO_SERVER/PLAINTEXT", plaintext)
    print("IN CLIENT.PY/FUNC:SEND_TO_SERVER/SEQ_NUM", session.seq_num)
    #msg has to be an encrypted success message from the server.
    #have to decrypt here, and then update the sequence numbering


    if status:
        print("Message successfully sent")
    else:
        print("Error: message could not send.")

if __name__ == "__main__":

    main()
