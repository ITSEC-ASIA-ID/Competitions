# An Offset Amongst Friends
tl;dr

ROT-like String Manipulation

### Solution

Participant are given a ELF binary file, we then try to load it into IDA to reverse engineer the application

```C
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  char s1[64]; // [rsp+0h] [rbp-C0h] BYREF
  char v5[64]; // [rsp+40h] [rbp-80h] BYREF
  char s2[56]; // [rsp+80h] [rbp-40h] BYREF
  unsigned __int64 v7; // [rsp+B8h] [rbp-8h]

  v7 = __readfsqword(0x28u);
  sub_128E(s2, a2, a3);
  printf("Enter the password: ");
  __isoc99_scanf("%s", s1);
  if ( !strcmp(s1, s2) )
  {
    sub_11C9(v5);
    printf("Correct! Here's your flag: %s\n", v5);
  }
  else
  {
    puts("Wrong password! Try again.");
  }
  return 0LL;
}
```

on the main function, we will be asked for a password and then a string comparation will be made on our input and a pre-processed string which is `s2` in this function, lets look how `s2` was processed on the function `sub_128E`

```C
unsigned __int64 __fastcall sub_128E(__int64 a1)
{
  int i; // [rsp+14h] [rbp-1Ch]
  char v3[14]; // [rsp+1Ah] [rbp-16h] BYREF
  unsigned __int64 v4; // [rsp+28h] [rbp-8h]

  v4 = __readfsqword(0x28u);
  strcpy(v3, "vompdl`nf`234");
  for ( i = 0; v3[i]; ++i )
    *(_BYTE *)(i + a1) = v3[i] - 1;
  *(_BYTE *)(i + a1) = 0;
  return v4 - __readfsqword(0x28u);
}
```

so `s2` will be the string `vompdl&#96;nf&#96;234` where every character ascii value will be decreased by 1, using a bit of programming we know that `s2` will be `unlock_me_123` after that function which is our needed password

```python
temp="vompdl`nf`234"
temp=''.join([chr(ord(i)-1) for i in temp])
print(temp)
```

putting that value in the program will print our flag

![Image](https://github.com/user-attachments/assets/3aca03ce-463c-4149-8497-592f3d4418b6)

actually we can delve a bit deeper into the function that will process the flag value which is `sub_11C9` and noticed that it's the same process as for the password but for the flag, we need to use the string `gmbh|d65426593642d22b87bfbb939f54918d~` and decrease it ascii value by 1

```C
unsigned __int64 __fastcall sub_11C9(__int64 a1)
{
  int i; // [rsp+1Ch] [rbp-34h]
  char v3[40]; // [rsp+20h] [rbp-30h] BYREF
  unsigned __int64 v4; // [rsp+48h] [rbp-8h]

  v4 = __readfsqword(0x28u);
  strcpy(v3, "gmbh|d65426593642d22b87bfbb939f54918d~");
  for ( i = 0; v3[i]; ++i )
    *(_BYTE *)(i + a1) = v3[i] - 1;
  *(_BYTE *)(i + a1) = 0;
  return v4 - __readfsqword(0x28u);
}
```

```python
temp="gmbh|d65426593642d22b87bfbb939f54918d~"
temp=''.join([chr(ord(i)-1) for i in temp])
print(temp)
```


