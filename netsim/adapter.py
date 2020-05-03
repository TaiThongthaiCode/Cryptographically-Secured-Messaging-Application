import pyDHE
import json
import shutil
import os
from netinterface import network_interface
from base64 import b64encode

class Adapter:

    def __init__(self, NET_PATH, OWN_ADDR):

        self.NET_PATH = NET_PATH
        self.OWN_ADDR = OWN_ADDR
        self.NETIF = network_interface(NET_PATH, OWN_ADDR)

    def listen(self):

        #TODO give an error message
        while True:
            status, msg = self.NETIF.receive_msg()
            if status:
                return status, msg

    def send(self, msg, dst):
        """
        @params: msg, dst
        """
        if self.NETIF.send_msg(dst, msg.encode('utf-8')):
            return True
        else:
            return False

    def send_public_key(self, dst):

        User = pyDHE.new()
        msg = str(User.getPublicKey())

        self.NETIF.send_msg(dst, msg.encode('utf-8'))

        return User

    #USER COMMANDS
    def create_header(self, type, command):
        header = {}
        header["from"] = self.OWN_ADDR
        header["type"] = type
        header["command"] = command
        header = json.dumps(header).encode('utf-8')

        return header

    def create_msg(self, header, ciphertext, tag):
        msg = {}
        msg["header"] = b64encode(header).decode('utf-8')
        msg["ciphertext"] = b64encode(ciphertext).decode('utf-8')
        msg["tag"] = b64encode(tag).decode('utf-8')
        msg = json.dumps(msg)

        return msg

    def getTitle(self, src_path):
        """
        Gets the title of the Document
        """
        title = ""
        len_path = len(src_path)-1
        while(src_path[len_path] != "/" and len_path >= 0):
            title = src_path[len_path] + title
            len_path -= 1

        return title

    def upload_file_helper(self, src_path):
        """
        Uploads the File
        """
        title = self.getTitle(src_path)
        print("TITLE: " + title)

        script_dir = os.path.abspath(src_path)
        file = open(script_dir)
        body = file.read()
        plaintext = title + "\n" + body
        plaintext = plaintext.encode('utf-8')
        return plaintext

    def mk_dir(self, path):
        """
        Making a new directory
        """
        if(path[-1] == "/"):
            path = path[:-1]
        os.mkdir(path)

    def del_directory(self, src_path):
        """
        Deletes an empty directory
        """
        os.rmdir(src_path)

    def del_file(self, src_path):
        """
        Deletes a file
        """
        os.remove(src_path)
