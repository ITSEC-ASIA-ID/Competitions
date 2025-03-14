# Ultimate Algorithm Factory

# 📊 Analysis

There are **four main features** in this system:

![Feature Overview](https://github.com/user-attachments/assets/43a305c3-bb08-4953-af2b-182588966764)

**1. Buying Algorithms**
- You can **purchase algorithms** using in-game money.
- The **purchase limit**:
  - Minimum: **1 money**
  - Maximum: **5 money**
- You **cannot** buy an algorithm if the cost is outside this range.

**2. Selling Algorithms**
- You can **sell the last algorithm** you purchased.
- This means only the **most recently bought algorithm** can be resold.

**3. Upgrading Algorithms (Delayed Execution)**
- You can **upgrade** an algorithm to **any** algorithm you previously bought.
- The upgrade increases the algorithm’s value by the requested amount.
- However, **the upgrade does not happen instantly**:
  - It follows a **delayed execution mechanism**.
  - The **delay is equal to the money spent on the upgrade** (measured in iterations).

**Delay Mechanism:**
- The **upgrade timer** runs in a loop for the same amount as the money spent.
- Example from the system:
  
  ![Delay Looping](https://github.com/user-attachments/assets/f4f76392-6839-4c85-8f36-d289cf483376)

- The upgrade takes effect **only after the delay is completed**.

**4. Winning Condition: Getting the Flag**
- The goal is to **reach more than 100 money**.
- Money is represented as **DFA**.
- The **normal gameplay mechanics** make it **impossible** to exceed **10 money**.

**Flag Requirement:**

![Flag Condition](https://github.com/user-attachments/assets/8b7a6e06-4eb9-4c37-8237-4ca994daa6af)


**Challenge: Breaking the Limit**

- Under normal conditions, it is **impossible** to exceed **10 money**.
- The **task** is to find a way to **bypass the limit** and reach **100+ money**.

# Solution

**Finding the Exploit**

I discovered that the **`inprogress_algorithm` address can be sold**. This allows us to **downgrade an algorithm to a lower-cost version**, effectively generating **infinite money**.

![Exploit Discovery](https://github.com/user-attachments/assets/50af55ec-af89-47f3-9791-280dca968eff)


**Exploiting the Vulnerability**

The **exploit strategy** follows these steps:

1. **Buy an algorithm** for **5 money** → **Current money: 5**
2. **Upgrade** the algorithm to **8 money** ( 5 money + 3 Money )
   - **There will be a delay loop (3 cycles)** → **Current money: 2**
3. During the **delay period**, perform these actions:
   - **Loop 1:** Sell the last algorithm → **Current money: 7**
   - **Loop 2:** Buy a cheaper algorithm (**cost: 1**) → **Current money: 6**
   - **Loop 3:** Sell the cheaper algorithm → **Current money: 14** ( Because the last algorithm is upgrade from 1 to 8 )

4. **Repeat the process** to continuously increase money.

**Snippet Exploit Script**

This sequence successfully **bypasses the money limit**:

```python
buy_algo(5)  # Buy an algorithm for 5 money

upgrade(0,3)  # Upgrade it with a delay of 3 loops

sell_algo()   # Sell the last algorithm
buy_algo(1)   # Buy a cheaper algorithm (1 money)
sell_algo()   # Sell the cheaper algorithm
```

**Results**

After running the exploit, the **DFA (money) exceeds 10**:
- **Final money: 14 DFA** (An increase of **4 DFA** per cycle)

![DFA Increase](https://github.com/user-attachments/assets/b16eb6e2-6823-401c-9317-66b9046b6bd4)

Simply **repeat the process** until the **money surpasses 100**.

**Final Execution**

After multiple iterations, we achieve **DFA > 100**, obtaining the **flag**!

![Final Run](https://github.com/user-attachments/assets/9f717750-6a36-4097-9fbb-b1f2cd42b926)


