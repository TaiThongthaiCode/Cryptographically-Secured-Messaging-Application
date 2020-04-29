"""
"""

import pyDHE
from netinterface import network_interface


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

    def _createFolder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' +  directory)
            

        # # Example
        # createFolder('./data/') 
