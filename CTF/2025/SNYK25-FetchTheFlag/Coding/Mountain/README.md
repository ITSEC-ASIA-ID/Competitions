
# Solution

The challenge involves **coding logic** to identify the **first year a mountain appeared** and its corresponding **height**.

**Understanding the Problem**
- Initially, the **JSON data** about the mountains **is not provided**.
- However, at the **end of the process**, the player **receives the mountain JSON**.
- The task is simple: **If a given mountain name appears, return its height and first recorded year**.

**Solution Approach**
1. **Parse the provided JSON** containing mountain data.
2. **Extract** the relevant details: 
   - **Mountain name**
   - **Height**
   - **First recorded year**
3. **Return the correct information** when queried.

Snippet json
```json
    {
        "name": "Labuche Kang",
        "height": "24,170",
        "first": "1987"
    },
    {
        "name": "Kirat Chuli",
        "height": "24,154",
        "first": "1939"
    },
    {
        "name": "Abi Gamin",
        "height": "24,131",
        "first": "1950"
    }
```
Solver script
```py
from pwn import *
import json

with open("mountains.json") as f:
    data = json.loads(f.read())

def find_height_year(name):
    for i in data:
        if name == i['name']:
            return f"{i['height'].replace(",","")},{i['first']}"
        
io = connect("challenge.ctf.games",31731)

io.sendlineafter(b": ",b"Y")

for i in range(50):
    io.recvuntil(b"first ascent year of ")
    name = io.recvuntil(b": ",drop=True).decode()
    answer = find_height_year(name)
    print(name,answer)
    io.sendline(answer.encode())

io.interactive()
```
