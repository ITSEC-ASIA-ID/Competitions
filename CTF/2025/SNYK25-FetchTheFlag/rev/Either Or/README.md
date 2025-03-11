# Either Or
tl;dr

Operation on string

### Solution

Participant are given a ELF binary file, we then try to load it into IDA to reverse engineer the application

```C
int __fastcall main(int argc, const char **argv, const char **envp)
{
  char s2[16]; // [rsp+0h] [rbp-D0h] BYREF
  char v5[64]; // [rsp+10h] [rbp-C0h] BYREF
  char s1[64]; // [rsp+50h] [rbp-80h] BYREF
  char v7[56]; // [rsp+90h] [rbp-40h] BYREF
  unsigned __int64 v8; // [rsp+C8h] [rbp-8h]

  v8 = __readfsqword(0x28u);
  strcpy(s2, "frperg_cnffjbeq");
  puts("Welcome to the Encoding Challenge!");
  printf("Enter the secret word: ");
  __isoc99_scanf("%s", v5);
  encode_input((__int64)v5, (__int64)s1);
  if ( !strcmp(s1, s2) )
  {
    decode_flag(v7);
    printf("Well done! Here's your flag: flag{%s}\n", v7);
  }
  else
  {
    puts("Not quite right. Keep trying!");
  }
  return 0;
}
```

so based on this main function, our input will be encoded and then compared to the string `frperg_cnffjbeq`, we can actually look into the `decode_flag` function directly ignoring the string comparing condition

```C
unsigned __int64 __fastcall decode_flag(__int64 a1)
{
  signed int i; // [rsp+1Ch] [rbp-34h]
  _QWORD v3[5]; // [rsp+20h] [rbp-30h] BYREF
  unsigned __int64 v4; // [rsp+48h] [rbp-8h]

  v4 = __readfsqword(0x28u);
  qmemcpy(v3, "$ruv&qz{qpstv puz#wrz&$ss w'$$z{", 32);
  for ( i = 0; (unsigned int)i <= 0x1F; ++i )
    *(_BYTE *)(i + a1) = *((_BYTE *)v3 + i) ^ 0x42;
  *(_BYTE *)(a1 + 32) = 0;
  return v4 - __readfsqword(0x28u);
}
```

as we can see we just need to do a xor operation to the string `$ruv&qz{qpstv puz#wrz&$ss w'$$z{` to get the flag, but lets not taking the easy route and look into the `encode_input` function

```C
_BYTE *__fastcall encode_input(__int64 a1, __int64 a2)
{
  _BYTE *result; // rax
  int i; // [rsp+1Ch] [rbp-4h]

  for ( i = 0; *(_BYTE *)(i + a1); ++i )
  {
    if ( *(char *)(i + a1) <= 96 || *(char *)(i + a1) > 122 )
    {
      if ( *(char *)(i + a1) <= 64 || *(char *)(i + a1) > 90 )
        *(_BYTE *)(i + a2) = *(_BYTE *)(i + a1);
      else
        *(_BYTE *)(i + a2) = (*(char *)(i + a1) - 52) % 26 + 65;
    }
    else
    {
      *(_BYTE *)(i + a2) = (*(char *)(i + a1) - 84) % 26 + 97;
    }
  }
  result = (_BYTE *)(i + a2);
  *result = 0;
  return result;
}
```

so this function will iterate each character of our input and then do something to the character based on some branching condition. We can rebuild this function and then map all possible character to the resprective encoded character

```python
import string

def encode_input(a):
    if a <=96 or a>122:
        if a<=64 or a>90:
            return chr(a)
        else:
            return chr((a-52)%26+65)
    else:
        return chr((a-84)%26+97)

charset=string.printable
mapped=dict()
need="frperg_cnffjbeq"
for i in charset:
    mapped[encode_input(ord(i))]=i
ans=""
for i in need:
    ans+=mapped[i]
print(ans)
```

and so we know that our secret word is "secret_password", we can enter it to get our flag

![Image](https://github.com/user-attachments/assets/5a620156-91c9-4edd-bc7d-78c181a2fe93)

