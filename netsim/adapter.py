"""
"""

import pyDHE
import json
import shutil
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

    # OS UTILITIES FUNCTIONS
    # https://www.pythoncentral.io/how-to-recursively-copy-a-directory-folder-in-python/

    def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)

    def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

    def _createFolder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' +  directory)
