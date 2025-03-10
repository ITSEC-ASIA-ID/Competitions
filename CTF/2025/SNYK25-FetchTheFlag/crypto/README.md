# Padding Gambit
tl;dr

Padding Oracle Attack + Binary Respresentation Using Chess

### Part 1 : Padding Oracle attack

At first we're given with a website in which we're asked to enter a code

![Image](https://github.com/user-attachments/assets/98953612-1055-45c1-9e26-6ed0ca554420)

later on the competition, the author actually give the source code of the application to avoid it being to guessy

```js
app.post('/api/submit/:token', (req, res, next) => {
  const urlToken = req.params.token;
  if (!urlToken) {
    return res.status(400).json({ error: 'Missing token in URL' });
  }

  const decryptionResult = decrypt(urlToken);
  if (!decryptionResult.success) {
    const err = new Error(`Decryption failed: ${decryptionResult.error}`);
    err.statusCode = 400;
    return next(err);
  }

  const submittedCode = req.body.code;
  if (!submittedCode) {
    return res.status(400).json({ error: 'Missing code in request body' });
  }

  if (submittedCode === secretCode) {
    res.json({ message: `Correct code! Flag: ${flag}` });
  } else {
    res.status(400).json({ error: 'Incorrect code' });
  }
});
```

based on this code, when we submit our code, it will also send our cookie token from the url parameter and then tried to decrypt it, if it failed to decrypt then it will send back "Decryption failed" alongside the error and if it's succesfully decrypted it will check if our submitted code is equal to the secret code on the server, if its not then it will send back Incorrect code and if it is then it will send back the flag.

We noticed the different response based on the decryption process and so we can use Padding Oracle Attack get the value of decrypted `urlToken` using our encrypted `urlToken`. All we need to do is first to get the token and then make a submit request to the server while bruteforcing possible value, and finally check the response of the service while supplying arbitrary `secretCode` as we want it to return `Incorrect code` if the decryption process succeed, here's the script that we used :

```python
import requests
from Crypto.Util.number import *
import json
import base64
from urllib.parse import unquote,quote_plus


def tambah(val,tambah):
    val = [long_to_bytes(val[i]^tambah) for i in range(len(val))]
    return b''.join(val)
f=requests.get("http://challenge.ctf.games:30189/api/token")
token = (f.json()['token'])
token = unquote(token)


msg=b""
dec=b""
temp=base64.b64decode(token)
blocks = [temp[i:i+16] for i in range (0,len(temp),16)]
fin_msg=b""
cnt_msg=0
for iv_cnt in range(0,len(blocks)-1):
    iv , ct = blocks[iv_cnt],blocks[iv_cnt+1]
    msg=b""
    dec=b""
    for j in range(1,17):
        blok = iv[:-j]

        for i in range(0,256):      
            payload_blok = quote_plus(base64.b64encode(blok+long_to_bytes(i)+tambah(dec,j)+ct))
            data={"code":"aa"}
            f=requests.post(f"http://challenge.ctf.games:30189/api/submit/{quote_plus(payload_blok)}",json=data)
            resp = f.json()
            # print(payload)
            print(resp)
            if "Incorrect" in resp['error']:
                temp = i^j
                dec=long_to_bytes(temp)+dec
                msg=long_to_bytes(iv[-j]^temp)+msg
                break
        print(msg)
    fin_msg +=msg
print(fin_msg)
```

### Part 2 : Binary Respresentation Using Chess

after that we got the `urlToken` which is a link to `https://pastebin.com/rzZMdkvs`, the pastebin is containing this text

```
would you like to play a game? 1PPPP3/2P1P3/1P3PP1/1PPP1P2/1P3PP1/2PP2P1/2PP1P1P/2P1P2P w - - 0 1
```

We noticed that it looks like FEN chess notation so we load it into chess.com analysis engine and we got this board configuration

![Image](https://github.com/user-attachments/assets/d7de3567-380f-4db5-9275-143e47c4c49a)

after a bit of time trying various possible solution for this, we noticed that this chess configuration looks like binary number representation which consist of 8 bits, set from left to right, so we interpret empty spaces as 0 and spaces that have pawn as 1 and so we got these binary number that each represent a character

```
01111000 = x
00101000 = (
01000110 = F
01110100 = t
01000110 = F
00110010 = 2
00110101 = 5
00101001 = )
```

and so we enter the code `x(FtF25)` and got the flag

![Image](https://github.com/user-attachments/assets/3188a75c-aff8-47ac-b721-975544b1fe6b)