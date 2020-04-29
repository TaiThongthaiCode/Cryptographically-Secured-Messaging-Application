#importing Crytodome for CTR CBC-MAC
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

#importing to convert DH Key into key of 16bytes for CCM Mode
import hashlib

class Session:

    def __init__(self, key):
        self.rec_num = 0
        self.send_num = 0

        #conversion of DH Key to 16 bytes

        key = str(key)
        key = key.encode('utf-8')[:16]
        self.key = key

    def encrypt(self, header, data):
        """
        @Param: Header - header in bytes
        @Param: data - Data to be encrypted, in bytes
        """

        nonce = self.rec_num.to_bytes(length=10, byteorder='big')

        cipher = AES.new(self.key, AES.MODE_CCM, nonce = nonce)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)


        return ciphertext, tag

    def decrypt(self, header, ciphertext, tag):
        """
        @Param: ciphertext - json formatted ciphertext
        """
        nonce = self.rec_num.to_bytes(length=10, byteorder='big')
        # b64 = json.loads(ciphertext)
        # json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
        # jv = {k:b64decode(b64[k]) for k in json_k}

        cipher = AES.new(self.key, AES.MODE_CCM, nonce=nonce)
        cipher.update(header)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
 