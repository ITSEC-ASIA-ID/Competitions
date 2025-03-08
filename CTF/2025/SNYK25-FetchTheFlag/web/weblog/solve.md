# Weblog
tl;dr
- SQL Injection retrive admin password hash (MD5) to gain RCE on admin panel

   
## Analyzing Source Code
We got another python web challenge, in the `app.py` we must be registered to interact with the website.
![image](https://github.com/user-attachments/assets/7ff1b3f8-5d52-47d0-96eb-edc66afc21c0)

This is the website where we can create/delete/view blog and search blog post
![image](https://github.com/user-attachments/assets/d69d168a-28c9-4541-b8d0-26d77e1b3d4d)

The most interesting file is `search.py` that contain `raw_query` where we can inject our SQL query to be executed from SELECT statement combined with LIKE
![image](https://github.com/user-attachments/assets/5eaa7843-7de9-4aaf-86c2-7bde12d99dbf)

And this is the database model that might be useful later.
![image](https://github.com/user-attachments/assets/fbaa3949-2d22-4877-bb32-0f951260e6e9)


## Exploit

Let's try with UNION injection (' union all select 1-- -), the website shows an error about different number of columns. 
If we enumerate the columns, the right value is 5 so we must change the payload to (' union all select 1,2,3,4,5-- -)
![image](https://github.com/user-attachments/assets/6456fd21-c41a-4754-b39f-d05a52223c74)

Yep, we got UNION based SQL Injection. We can retrive admin username and the hashed password from users table. 
![image](https://github.com/user-attachments/assets/1d204bde-2922-4c67-82a8-ef92cc5a1d16)

`' union all select 1,concat(username,0x20,password),3,4,5 from users-- -` luckily this is a whitebox challenge so we don't need to enumerate the table & column name from INFORMATION_SCHEMA.
Let's try to crack the hash using crackstation.
![image](https://github.com/user-attachments/assets/34d88e97-285b-41e8-8e13-1de46dc80bfa)

We got the admin password `admin_password`! *note: The password for the production/challenge box is different. This write-up was written after the competition ended.*
![image](https://github.com/user-attachments/assets/a5367f3b-1198-4cf8-b468-cfa21387eeb0)

After logging in as admin we can access the admin panel
![image](https://github.com/user-attachments/assets/22606b3f-c83f-40ff-9837-9533ea2e2fb5)


This is the `admin.py` code, where we can inject our payload for RCE because of `os.popen()` function! but the command must start with the value of `DEFAULT_COMMAND` variable `echo 'Rebuilding database...' && /entrypoint.sh`
and there are several banned characters.
![image](https://github.com/user-attachments/assets/8009f6d6-e0b1-406e-9bfc-b564eb70803c)

Time to perform OS command injection attack, we can bypass the banned character with semi-colon (;) and we got the flag!
![image](https://github.com/user-attachments/assets/7d19a075-314f-4698-82ce-2ef0ac86ea32)

![image](https://github.com/user-attachments/assets/51f8264b-c2f4-4495-a401-7aabe15ba0f9)



