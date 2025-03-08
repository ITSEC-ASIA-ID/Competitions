# Unfurl
tl;dr

- SSRF by bruteforcing admin port

## Analyzing Source Code 

We get an application that will create a curl request. Let's analyze the source code.
![image](https://github.com/user-attachments/assets/2dd973c9-9d5c-48f3-9a73-083b5aa14287)

This is the `/unfurl` route that will "curl"-ing request and will parse the image if contains any `rel="icon" / property="og:image"` and the HTML content of the URL.
![image](https://github.com/user-attachments/assets/dd25a327-064b-4782-a3a0-ffbe0475f494)
![image](https://github.com/user-attachments/assets/07f0ac26-e997-45aa-b432-a8bffe8ccb60)
Tried to test the parse image function
![image](https://github.com/user-attachments/assets/65860695-9689-471e-b0fa-1991783531fa)

`admin.js` got something interesting which is `getRandomPort()` function that will be returning random port when the box is running.
We can try to brute force the port and access the admin page.
![admin.js](https://github.com/user-attachments/assets/1b8eccba-b3f1-4eb6-afea-2e09d507429d)

`adminRoutes.js` has several interesting endpoints the most interesting is `/execute`
![image](https://github.com/user-attachments/assets/aaed86f3-831c-48bf-a079-09dd10ef92f8)

on `execute` route, we can run a command with ?cmd parameter that will be executed with `exec` function but there is a twist the IP address must be equal to `127.0.0.1` 
![image](https://github.com/user-attachments/assets/22fd0167-7ada-4eeb-a3a6-a9f0e0efed34)

## Exploiting

After we analyze the source code then we proceed to bruteforcing the port using BurpSuite Intruder and we got a hit to admin page on port 2310
![image](https://github.com/user-attachments/assets/c7b2da55-ff47-4daa-b874-004fd55c8391)

![image](https://github.com/user-attachments/assets/122ce73e-fb3d-443a-bfa6-6fdabbcf0f11)

And executing the `execute` route with `cmd` parameter to obtain the flag.
![image](https://github.com/user-attachments/assets/20bd54ca-de4b-4770-9aba-7ffff930187d)
