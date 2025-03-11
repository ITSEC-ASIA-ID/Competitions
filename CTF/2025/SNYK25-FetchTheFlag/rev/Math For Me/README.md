# String Me Along
tl;dr

Number checker in ELF file

### Solution

participants are given a ELF binary file, upon receiving it we tried to run it and it ask for a `special number` and so we load it into IDA to reverse engineer the program

```C
int __fastcall main(int argc, const char **argv, const char **envp)
{
  unsigned int v4; // [rsp+8h] [rbp-48h] BYREF
  int i; // [rsp+Ch] [rbp-44h]
  char v6[37]; // [rsp+10h] [rbp-40h] BYREF
  char v7[19]; // [rsp+35h] [rbp-1Bh] BYREF
  unsigned __int64 v8; // [rsp+48h] [rbp-8h]

  v8 = __readfsqword(0x28u);
  puts("Welcome to the Math Challenge!");
  printf("Find the special number: ");
  __isoc99_scanf("%d", &v4);
  qmemcpy(v6, "flag{", 5);
  if ( (unsigned int)check_number(v4) )
  {
    for ( i = 5; i <= 36; ++i )
      compute_flag_char(v6, (unsigned int)i, v4);
    strcpy(v7, "}");
    printf("Congratulations! Here's your flag: %s\n", v6);
  }
  else
  {
    puts("That's not the special number. Try again!");
  }
  return 0;
}
```

based on this Main function, we need to input a number and then it will be checked using the function `check_number`, we then looked into the function

```C
_BOOL8 __fastcall check_number(int a1)
{
  return (5 * a1 + 4) / 2 == 52;
}
```

so we need to find the value `a1` in which after putting it into the function will be equal to `52`, we can find this value using some basic math 

![Image](https://github.com/user-attachments/assets/24a24132-a8fc-4dc0-8a70-680faf61d010)

and our secret number will be `20` and so if we enter the number we will get our flag

![Image](https://github.com/user-attachments/assets/d93191f3-bffa-42e8-8dca-aee49bc47c48)