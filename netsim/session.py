#importing Crytodome for CTR CBC-MAC
import os
import json
from base64 import b64encode
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

#importing to convert DH Key into key of 16bytes for CCM Mode
import hashlib

class Session:

    def __init__(self, key):
        self.seq_num = 0

        #conversion of DH Key to 16 bytes
        key = str(key)
        key = key.encode('utf-8')[:16]
        self.key = key

    def encrypt(self, header, data):
        """
        @Param: Header - header in bytes
        @Param: data - Data to be encrypted, in bytes
        """

        copyheader = json.loads(header.decode('utf-8'))
        ctr = copyheader["nonce"]
        nonce = ctr.to_bytes(length=10, byteorder='big')

        cipher = AES.new(self.key, AES.MODE_CCM, nonce = nonce)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        return ciphertext, tag

    def decrypt(self, header, ciphertext, tag):
        """
        @Param: ciphertext - json formatted ciphertext
        """
        copyheader = json.loads(header.decode('utf-8'))
        ctr = copyheader["nonce"]

        if ctr > self.seq_num:
            self.seq_num = ctr

        nonce = self.seq_num.to_bytes(length=10, byteorder='big')

        cipher = AES.new(self.key, AES.MODE_CCM, nonce=nonce)
        cipher.update(header)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        return plaintext

    def create_header(self, command, OWN_ADDR, nonce=0, success=None):
        header = {}
        header["from"] = OWN_ADDR
        header["command"] = command
        header["nonce"] = nonce
        header["success"] = success
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
        if(src_path[len_path] == "/"):
            len_path -= 1
        while(src_path[len_path] != "/" and len_path >= 0):
            title = src_path[len_path] + title
            len_path -= 1

        return title

    def back_folder(self, src_path):
        if(src_path[-1] == "/"):
            src_path = src_path[:-1]
        title = self.getTitle(src_path)
        src_path = src_path.replace(title, '')
        print("SRC_PATH" + src_path)
        return src_path

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

    def parse_msg(self, msg):
        msg = json.loads(msg.decode("utf-8"))
        header = b64decode(msg['header'])
        ciphertext = b64decode(msg['ciphertext'])
        tag = b64decode(msg['tag'])

        #plaintext in bytes
        plaintext = self.decrypt(header, ciphertext, tag)
        plaintext = plaintext.decode("utf-8")
        header = json.loads(header.decode("utf-8"))

        return header, plaintext

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
