# Plantly
tl;dr

Flask SSTI to RCE on custom field

### Analyzing Source Code

On store.py, we got several endpoint route to list all of the plants and add we can purchase some plants. 
![image](https://github.com/user-attachments/assets/659ce43a-a6c1-426f-9771-4a8ce76a4b23)
As we can see here, on /receipt route there is a **render_template_string** function that is vulnerable to SSTI. By adding custom order, we can inject the payload to gain RCE.
![image](https://github.com/user-attachments/assets/e58e0fbb-6a45-469d-b78f-07b0a19ed70e)

### Exploit
After inserting SSTI payload ***{{7\*7}}*** for custom order and follow throught the process until receipt endpoint, the payload is executed successfully indicated with *49* on custom request field.
![image](https://github.com/user-attachments/assets/7dcd7290-eb00-4023-a8a6-f44c21d4ca55)

![image](https://github.com/user-attachments/assets/1badb38f-67ca-434e-89c7-fc1de9402203)

By inserting os.popen().read() template for retrieving the flag and then executing the checkout and receipt endpoints, eventually we will got the flag on the receipt!
![image](https://github.com/user-attachments/assets/5b704ec7-bf24-48ba-86b0-95929ad7af15)

![image](https://github.com/user-attachments/assets/3b51ab88-8161-4ea3-ba90-e15c9a50783e)
