


Within the loomRoom function, a buffer overflow exists in the src variable; however, altering the return address is not feasible.


# Initial Analysis (Decompilation)

The writer utilized the IDA Pro decompiler to facilitate a clearer understanding of the program's flow within the output code.

The executable file presents four main features:
1. Call loomRoom and return data `dest`, 
2. Print data from variable `v8` (the data inputed from no.1)
3. Need value a variable `aThisisnotthepa` to call fatesRoom
4. just exit program

# Vulnerability 

A noteworthy vulnerability lies in an unused function named theVoid. 
There one function never called is `theVoid`. This function appears to be designed to display a flag, so the write will assume thats the objective is successfully call function `theVoid`.

in function loomRoom, there are have buffer overflow at variable src but cann't change return address.

```
char src[8]
...
fgets(src, 286, _bss_start);
```

in function fatesRoom, there are also have buffer overflow and can change return address.
```
char dest[8];
...
strcpy(dest, a1);
```

# Exploit

First, you need to locate the method to call `fatesRoom` function. Following that, you can execute any function, such as `theVoid` function. What you require is the value from the `s2` variable.

A buffer overflow in `loomRoom` function, can be used to alter the value of `dest` variable to to your desired value, in the end of function, the `dest` variable will serve as a return value. 
```
...
v8 = loomRoom(v8, v4);
...
```
this mean that variable `dest` same as variable `v8`

After that feature number 2 can print variable `v8`, so you have abritary leak address.
```
printf("%s", v8);
```

in `fatesRoom` function , you can just do ret2win(return to win) to call `theVoid`

Run exploit 
```
└─# python2 solve.py      
[*] '/root/Desktop/github/CTF/TenableCTF2023/Reversing - Pwns/Skiddyana Pwnz and the Loom of Fate/loom'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Opening connection to 0.cloud.chals.io on port 33616: Done
[*] Switching to interactive mode


=============================================================================
Choose your next move:

1) Enter the room of the loom
2) Read the wall of prophecy
3) Enter the room of the fates
4) leave

> 

=============================================================================

You enter the room of the loom, and see the loom of fate before you. You can etch a prophecy into the futre, or leave the future alone.
1) Prophesize
2) Leave

> 

=============================================================================
Choose your next move:

1) Enter the room of the loom
2) Read the wall of prophecy
3) Enter the room of the fates
4) leave

> 

Before you is a large stone door. As you behold it, you hear a voice inside of your head.


Speak the unpronouncable phrase to pass to the room of fates : 

> 

=============================================================================

You enter the room of fates and see the tapestry of reality laid out before you.
The voice in your head returns:

'Are you willing to force your prophecy onto the past? To corrupt this reality to find what you seek?'

1) Yes
2) No

> 
You stretch the fabric of this reality, its premise worn thin.

...th...this is what you destroyed reality for?
Ok. Well. It's yours.

flag{d0nt_f0rg3t_y0ur_h4t}
```
## Flag

Flag : `flag{d0nt_f0rg3t_y0ur_h4t}`