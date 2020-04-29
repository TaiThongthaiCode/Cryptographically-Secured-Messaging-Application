"""
File is only for testing

"""
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def round3():
    header = b"header"
    data = b"secret"
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CCM)
    cipher.update(header)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
    json_v = [ b64encode(x).decode('utf-8') for x in cipher.nonce, header, ciphertext, tag ]
    result = json.dumps(dict(zip(json_k, json_v)))
    print(result)

def round2():

    dict = {"poo": "poop"}
    print(type(json.dumps(dict)))
    print(json.dumps(dict))




def round1():
    #ENCRYPING 
    header = b"server|f|success"
    data = b"secret"

    i = 6


    key = get_random_bytes(16)
    print(key)
    print(int.from_bytes(key, byteorder='big'))
    cipher = AES.new(key, AES.MODE_CCM, nonce=i.to_bytes(length=10, byteorder='big'))

    cipher.update(header)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    print(cipher.nonce)
    print(ciphertext)
    print(tag)


    #DECRYPTING 
    cipher2 = AES.new(key, AES.MODE_CCM, nonce = i.to_bytes(length=10, byteorder='big'))
    cipher2.update(header)
    plaintext = cipher2.decrypt_and_verify(ciphertext, tag)

    print(plaintext)


round3()