The writer found the way make the key bit is 1
```
state_list = [[1,1]]*1024
basis_list = ["H"]*1024
```
make value state to 1, then bit will be added '1'

i don't know why it is work, actually the writer set state_list to random value.

run solver
```
└─# python solver.py         
b'flag{d0nT_T0uch_QB17s_ar3_FraG1l3}'
```
# FLAG
`flag{d0nT_T0uch_QB17s_ar3_FraG1l3}``