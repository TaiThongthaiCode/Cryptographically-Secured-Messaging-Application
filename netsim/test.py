"""
File is only for testing

"""
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


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