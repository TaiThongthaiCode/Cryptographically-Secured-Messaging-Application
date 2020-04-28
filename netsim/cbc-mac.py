#importing Crytodome for CTR CBC-MAC
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encryption(header, data, key):
    """
    @Param: Header - header in bytes
    @Param: data - Data to be encrypted, in bytes
    @Param: key - the Diffie-Hellmen Key
    """
    cipher = AES.new(key, AES.MODE_CCM)
