# xfil
xfil is a tool that performs blind XPath exploitation and data exfiltration. This tool is created for penetration testers performing authorized security assessments.

## Usage

```
usage: xfil.py [-h] [-q] --url URL --method {GET,POST} --param PARAM [--success-text SUCCESS_TEXT] [--failure-text FAILURE_TEXT] [--success-code SUCCESS_CODE]
               [--failure-code FAILURE_CODE] [--post-data POST_DATA] [--content-type {application/json,application/x-www-form-urlencoded,multipart/form-data}] [--headers HEADERS] [-v]

options:
  -h, --help            show this help message and exit
  -q, --quiet           Suppress banner
  --url URL             Target URL
  --method {GET,POST}   HTTP method
  --param PARAM         Vulnerable parameter name
  --success-text SUCCESS_TEXT
                        Text indicating successful injection
  --failure-text FAILURE_TEXT
                        Text indicating failed injection
  --success-code SUCCESS_CODE
                        HTTP status code indicating success
  --failure-code FAILURE_CODE
                        HTTP status code indicating failure
  --post-data POST_DATA
                        Additional POST data in format "key1=value1&key2=value2" or JSON string
  --content-type {application/json,application/x-www-form-urlencoded,multipart/form-data}
                        Content-Type header for POST requests
  --headers HEADERS     Additional headers in JSON format or "Key: Value" pairs separated by semicolons or newlines
  -v, --version         Show program version
  ```

  Note: If the `--success-text` argument is used, `--failure-text` must also be specified. The `--failure-text` argument can be used alone.