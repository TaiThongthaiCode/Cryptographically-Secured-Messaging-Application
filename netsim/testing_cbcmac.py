from session import *

import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def main():
    data = b'Hi There'
    header = b'Greeting'
    key = 7635592827986435815495973395650528553075776550682037235668176347199964190389564705235482361428940927362015314916853518651471989336810432962158737784238403268508062988911743545600071807663217454678111573927968389381124246206830929647391960037077980978844160811129695189522643335652737008051520556139609443198907623325384104173684380660947584754068843044801716213680082245188213901318273721052052587873217612861737931022110394819662251810430549060503380301155210985303403525967289602149159766097739105672315816720913966908072507067651840319435018214264895314847003538662431495298197693160598501301717073716253900720927

    key = str(key)

    key = key.encode('utf-8')[:16]

    print(key)
    print(type(key))

    s = Session(key)

    header, ciphertext, tag = s.encryption(header, data)
    print(ciphertext, tag)

    result = s.decryption(header, ciphertext, tag)

    print(result)
    




if __name__ == "__main__":
    main()