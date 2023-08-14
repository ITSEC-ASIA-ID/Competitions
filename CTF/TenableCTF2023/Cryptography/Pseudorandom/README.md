# Pseudorandom - Cryptography

## Ideas

Given a code like this and a snippet of the output.

```python
import random
import time
import datetime  
import base64

from Crypto.Cipher import AES
flag = b"find_me"
iv = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"

for i in range(0, 16-(len(flag) % 16)):
    flag += b"\0"

ts = time.time()

print("Flag Encrypted on %s" % datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M'))
seed = round(ts*1000)

random.seed(seed)

key = []
for i in range(0,16):
    key.append(random.randint(0,255))

key = bytearray(key)


cipher = AES.new(key, AES.MODE_CBC, iv) 
ciphertext = cipher.encrypt(flag)

print(base64.b64encode(ciphertext).decode('utf-8'))

#Flag Encrypted on 2023-08-02 10:27
#lQbbaZbwTCzzy73Q+0sRVViU27WrwvGoOzPv66lpqOWQLSXF9M8n24PE5y4K2T6Y
```

The solution is straightforward, but kinda guessy for a while since there are possibilities that the timezone is different, it turns out the `tz` follows the `EDT` format.

`AES` decryption is done with the same `IV` and the guessed `key` that is needed to be brute-forced throughout the time interval.

```python
import random
import time
import datetime  
import base64,string

# Flag Encrypted on 2023-08-02 10:27
# lQbbaZbwTCzzy73Q+0sRVViU27WrwvGoOzPv66lpqOWQLSXF9M8n24PE5y4K2T6Y
from Crypto.Cipher import AES
iv = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
# print(iv)
# print(time.time())
# print("Flag Encrypted on %s" % datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M'))
# start = 1690972020*1000
# start = int(datetime.datetime(2023,8,1,23,27).timestamp())*1000
for j in range(0,24):
    start = int(datetime.datetime(2023,8,2,j,26).timestamp())*1000
    end = int(datetime.datetime(2023,8,2,j,28).timestamp())*1000
    # print(start)
    flag = base64.b64decode("lQbbaZbwTCzzy73Q+0sRVViU27WrwvGoOzPv66lpqOWQLSXF9M8n24PE5y4K2T6Y")
    for i in range(start, end):
    #   seed = i
        random.seed(i)
        key = []
        for _ in range(0,16):
            key.append(random.randint(0,255))
        key = bytearray(key)
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv) 
            ciphertext = cipher.decrypt(flag)
            if ciphertext.endswith(b'\x00\x00'):
               print(i, ciphertext)
            # if all(char in string.printable for char in ciphertext.replace(b'\x00',b'')):
            #   print(i, ciphertext)
            if b"flag" in ciphertext:
                print(i, ciphertext)
                exit()
            # print(i, ciphertext)
        except Exception as e:
            continue
```

Eventually, we'll get the decrypted flag.

![](image/solved.png)


## Flag

flag{r3411y_R4nd0m_15_R3ally_iMp0r7ant}
