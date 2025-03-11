# String Me Along
tl;dr

Strings operation on binary file

### Solution

Participant are given a ELF binary file, based on this challenge name, we first tried to directly do `strings` command to find the strings on this file

![Image](https://github.com/user-attachments/assets/0463c9f8-7669-41a6-a0ed-c7ab68d0457d)

based on these string, we assume that the correct password will be `unlock_me_123` so we try to input it into our program and we got the flag

![Image](https://github.com/user-attachments/assets/a8006bdb-56c5-4511-854e-110e9bb89b77)

on the side notes, we can actually see our flag too upon doing the strings command which are separated by newlines

![Image](https://github.com/user-attachments/assets/4036b6d5-d7f8-44b5-bc2d-ea1f6b4ff129)