# Calculator 
I don't think this is a challenge binex but more seems misc python jail

# Analysis

You have a program that executes Python code using eval(), but with strict limitations:
- The input cannot contain any alphabetic characters (both uppercase and lowercase).
- The input cannot contain the underscore (_) symbol.

```py
import sys

def simple_calculator():
    print("Welcome to the Simple Calculator!")
    print("Enter a mathematical expression:", end=' ')
    expression = input()
    sys.stdin.close()
    try:
        blacklist = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
        for x in expression:
            if x in blacklist:
                print(f"{x} is not allowed!")
                exit()
        result = eval(expression)
        print(f"The result is: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_calculator()
```

However, the goal is to bypass these restrictions and execute shell commands, such as using os.system(input).

# Solution

The challenge restricts the use of alphabetic characters (A-Z, a-z) and the underscore (_) symbol in the input. However, we can bypass these limitations using Unicode representations and the chr() function.

1. Bypassing Alphabetic Character Restrictions

Alphabetic characters can be replaced with their Unicode equivalents from the Mathematical Alphanumeric Symbols table.
For example, o can be replaced with 𝐨 or 𝗈, which visually resemble o but are technically different Unicode characters.

2. Bypassing the Underscore (_) Restriction

Since there's no direct Unicode equivalent for _, we use chr(95) instead.
chr(95) dynamically generates the underscore character, bypassing the filter.

Since there are no length restrictions, we can generate a longer payload to obfuscate detection further.

the payload `__import__("os").system("/bin/sh")` will be inside eval()

Injecting the Payload into the Challenge

Once the generated payload is ready:
![image](https://github.com/user-attachments/assets/f4ef7c07-8f67-46a5-9501-bc64f72c195c)

Copy the generated payload.

Input it into the challenge.

Execute it, and a shell should spawn.
![image](https://github.com/user-attachments/assets/a4aefe2a-dbf8-4995-93b1-4c86dad1cdf5)


