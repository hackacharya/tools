#!/usr/bin/env python3 
#
# Copyright @ hackacharya 2024
#
# MIT License. 
#
# A simple tool to get a list of URLs and headers from a CSV file
# and and genreate http to a given webserver in sequence
#
# 
# example

#./injector.py --url-prefix https://api.example.org  --debug 
#./injector.py --url-prefix https://api.example.org  --request-details-csv myreqs.csv
#
# TODO
#  1-parallel
#  2-rate
#  3-random values in bodies and urls
#  4-store cookies against their domain, allow sending to different domains in one run.
#  5-save cookies across runs.
#  7-support 4xx,5xx etc in expectedstatus
#  8-andle interrupts properly
#
import csv
import requests
import argparse
import json
import time
import os
import re
import signal
import sys



MY_NAME="injector/1.5.1"
g_stop_processing = False;
g_debug = False;
g_show_cookies = False;

def signal_handler(sig, frame):
    global g_stop_processing;
    g_stop_processing = True;



# read_request_details_csv
#
# Read CSV file and return a list of dictionaries
# CSV Format
#
# Note:This header is required.
#
# Testcase ID,HTTP Method,URL,Headers,Cookies,Body
# Headers = "Name=value,Name2=value2,name3=value3" - use double quotes
# Cookies - "name1=value1,name2=value,..." - within double quotes
# Body - "{ value:xyz , blah }" or  @filepath
#
# You can use env variables in the values for Headers, Body
# remember to export your envs from your shell for thigns such as
# tokens etc.
# 
#
# Test Data File Smple CSV file
#
# Use Quotes for headers with literal commas in them
# comma is field separator
#
# TC001,GET,https://www.example.org,,,,
# TC002,POST,https://api.example.org,"Content-Type=application/json,Authorization=Bearer abc123,X-Custom-Header=value","session_id=abc123, user_id=xyz456",
# TC004,PUT,https://api.example.org/users/123,"Content-Type=application/json,Authorization=Bearer abc123",,,
# TC005,DELETE,https://api.example.com/posts/456,"Authorization=Bearer abc123","post_id=456, user_id=xyz456",
# ---------------------------------------------
def read_request_details_csv(file_path):
    data = []
    if not os.path.isfile(file_path):
        return None;
    with open(file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # remove commented lines.
            if any(value and isinstance(value, str) and value.strip().startswith('#') for value in row.values()):
                continue
            data.append(row)
    return data

# replace_variables
# Replace variables in a string with their environment values
# Allow use of env values in header and body values
# Remember to export the env values use ${ENV_VARIABLE}
# --------------------------------------------------------------
def replace_env_variables(value):
    # Use regex to find all occurrences of ${VARIABLE_NAME}
    return re.sub(r'\$\{(\w+)\}', 
                  lambda match: os.environ.get(match.group(1), ''), value)

# Headers column example
# "Content-Type=application/json,Authorization=Bearer abc123,X-Custom-Header=value/34"
# returns dict
def parse_namecolonvalue_str(namecolonvalue_str):
    name_value_dict = {}

    if not namecolonvalue_str:
        return name_value_dict;

    nev_str =  namecolonvalue_str.strip().strip('"').strip()
    if len(nev_str) == 0:
        return name_value_dict;

    # Allow and handle escaped commans handle escaped commas inside header values
    # Allow and handle handle escaped is-equial-to within values.
    # Example:
    # The following should produce two headers Accept and Content-Type only 
    # with their proper values.
    #
    #  multieq = "Accept=text/html\,application/xhtml+xml\,application/xml;q\=0.9;image/avif\,image/webp\,image/png\,image/svg+xml\,*/*;q\=0.8,Content-Type=application/json"
    esc_nev = nev_str.replace("\\,","${kMa}").replace("\\:", "${esCol}")
    pairs = esc_nev.split(',')
    for pair in pairs:
        try:
            key, value = pair.split(':', 1)
            new_val = value.replace("$esCol$", ":").strip() # kMa replace taken care of by replace_envars
            name_value_dict[key.strip()] = replace_env_variables(new_val);
        except ValueError:
            print("ignoring .. ", pair)
            continue;
    return name_value_dict

# read_cookies_from_json
# Read cookies from a JSON file for use with reqeusts
#
# Cookies File Format.
# Firefox cookies export from "COpy" All in web developer mode 
#{
#"Request Cookies": {
#	"_ga": "GA1.1.531067080.1713252297",
#	"_ga_0C4M1PWYZ7": "GS1.1.1713252296.1.1.1713252350.0.0.0",
#	"_ga_CNEYRJBCNQ": "GS1.1.1718699892.6.0.1718699892.0.0.0",
#	"_ga_K2SPJK2C73": "GS1.1.1713252297.1.1.1713252350.7.0.0",
#	"_ga_T11SF3WXX2": "GS1.1.1713252297.1.1.1713252350.7.0.0"
#}
#
def read_cookies_from_json(file_path):
    if not os.path.isfile(file_path):
        return None;
    with open(file_path, 'r') as file:
        cookies_data = json.load(file)
        return cookies_data.get("Request Cookies", {})

# Send a reqeust
# Take trustchain, cleintcert, key 
# Take method, URL , headers, body
#
#    return response, cookies, response_time
#
def send_https_request(sendreq, method, url, headers, cookies, use_configured_cookies, timeout, verify, cert, key, body):
    # Create a CookieJar to store cookies
    cookie_jar = requests.cookies.RequestsCookieJar()

    # Add configured cookies to the cookie jar
    if use_configured_cookies:
        for cookie in cookies:
            cookienamevalue = cookie.split('=', 1)
            if len(cookienamevalue) == 2:
                cookie_jar.set(cookienamevalue[0], cookienamevalue[1])
            # this is for the case where cookies can have '=' in them
            # cookie_name, *cookie_value = cookie.split('=')
            #cookie_jar.set(cookie_name, cookie_value.join('=')) 


    exception = False;
    error_str = None
    start_time = time.time()
    response = None;
    try:
       if g_debug:
            if sendreq:
                print(f"Request ->\n{method} {url}")
            else:
                print(f"Would be Request ->\n{method} {url}")
            if headers:
                for hkey, hvalue in headers.items():
                    print(f"{hkey}: {hvalue}")
            print(" ")
            if body:
                print(body)
            if cookies and g_show_cookies:
                print("cookies:", cookies)
       if sendreq:
            response = requests.request(method,url,headers=headers, cookies=cookie_jar, timeout=timeout / 1000, verify=verify, cert=(cert, key) if cert and key else cert,data=body) 
            # Print response details if debug is enabled
            if g_debug:
                print("\n\nResponse ->\n", response.status_code)
                print(" ")
                if response.text:
                    print(response.text)
                    print("...")
    except requests.exceptions.Timeout:
        exception = True;
        error_str = "Timeout"
    except requests.exceptions.SSLError as e:
        exception = True;
        error_str = "SSLError"
    except requests.exceptions.InvalidHeader:
        exception = True;
        error_str = "InvalidHeader"
    except Exception as e:
        exception = True;
        error_str = str(e);

    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000  

    if exception:
        return None, error_str, response_time_ms
	
    # Save for use in the next request 
    if response:
        for cookie in response.cookies:
            cookies.append(f"{cookie.name}={cookie.value}")

    return response, cookies, response_time_ms

#multieq1 = '"Accept=text/html\,application/xhtml+xml\,application/xml;q\=0.9;image/avif\,image/webp\,image/png\,image/svg+xml\,*/*;q\=0.8,Content-Type=application/json"
#multieq2 = "Accept=text/html\,application/xhtml+xml\,application/xml;q\=0.9;image/avif\,image/webp\,image/png\,image/svg+xml\,*/*;q\=0.8,Content-Type=application/json"

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Send HTTPS requests using CSV data.')
parser.add_argument('--parse-only', action='store_true', default=False, help='Only parse the input and show what will happen')
parser.add_argument('--url-prefix', type=str, default='', help='String to prefix to all URL strings')
parser.add_argument('--start-from', type=str, default='', help='Skip all reqeust until this Testcase ID')
parser.add_argument('--count', type=int, default=0, help='Process only count number lines/cases and stop')
parser.add_argument('--request-details-csv', default='request-details.csv', help='Name of CSV data file, default request-details.csv')
parser.add_argument('--use-configured-cookies', action='store_true', default=True, help='Use configured cookies in addition to received cookies, default on')
parser.add_argument('--cookie-file', type=str, help='Path to JSON file containing request cookies, default cookies.json')
parser.add_argument('--timeoutms', type=int, default=10000, help='Timeout for requests in milliseconds, default 10s')
parser.add_argument('--trust-chain', type=str, help='Path to custom trust chain file')
parser.add_argument('--client-cert', type=str, help='Path to client certificate file')
parser.add_argument('--client-key', type=str, help='Path to client private key file')
parser.add_argument('--skip-tls-verification', action='store_true', help='Skip TLS verification failures')
parser.add_argument('--requests-per-second', type=float, default=1.0, help='Number of requests to send per second')
parser.add_argument('--debug', action='store_true', default=False, help='Enable debug output for requests and responses')
parser.add_argument('--show-cookies', action='store_true', default=False, help='In debug output show cookies also')
args = parser.parse_args()

g_debug = args.debug;
g_show_cookies = args.show_cookies;
g_num_tests = args.count;
g_parse_only = args.parse_only
request_details = read_request_details_csv(args.request_details_csv)

if request_details == None:
    print("Request details file not found.")
    sys.exit(2)

# Export a cookies from a request from web dev tools on your browser 
# and use the json - see format above, or create one manually.
initial_cookies = []
if args.cookie_file:
    initial_cookies_dict = read_cookies_from_json(args.cookie_file)
    if initial_cookies_dict != None:
        initial_cookies = [f"{name}={value}" for name, value in initial_cookies_dict.items()]

# support for self signed certs and such.
verify = args.trust_chain if args.trust_chain else True
if args.skip_tls_verification:
    verify = False

testcase_results = {}
delay_between_requests = 1.0 / args.requests_per_second  


# Some way to skip a set of tests
skip_processing = False;
if len(args.start_from.strip()) > 0:
    skip_processing = True

signal.signal(signal.SIGINT, signal_handler) 

# Needed for our comm and colon escapes
os.environ["kMa"] = ','
os.environ["esCol"] = ':'

for row in request_details:
    if g_stop_processing:
        break;
    testcase_id = row['Testcase ID']
    http_method = row['HTTP Method']
    expected_statuses_str = ""
    try:
        expected_statuses_str = row['Expected Statuses']
    except KeyError:
        pass 
    request_url = row['URL']
    all_headers = row['Headers']
    all_cookies = row['Cookies']
    usr_body = row['Body']
    # skip until we find the test case marked.
    if testcase_id.strip() == args.start_from.strip():
        skip_processing = False
    if skip_processing:
        continue;
    expected_statuses=[];
    try:
        expected_status_arr=expected_statuses_str.strip().split("|")
        expected_statuses = [int(s.strip()) for s in expected_status_arr if s.isdigit()]
    except Exception as e:
        pass

    # if no prefix is specified and a commandline prefix is provided use it. 
    if not request_url.startswith(('http://', 'https://')):
        request_url = args.url_prefix + request_url.strip()

    request_headers = parse_namecolonvalue_str(all_headers)
    request_headers["User-Agent"] = MY_NAME;
   
    request_cookies = []
    if all_cookies:
        # TODO split on comma?
        request_cookies.append(all_cookies.strip('"'))

    # a way to provide bodies.
    raw_body = None
    if usr_body:
        body_value = usr_body.strip().strip('"')
        if body_value.startswith('@'): # filename
            filename = body_value[1:]
            if os.path.isfile(filename):
                with open(filename, 'r') as file:
                    raw_body = file.read()
            else:
                print(f"{testcase_id}, Error: File '{filename}' not found.")
                continue  # Skip this request line if the file is not found
        else:
            raw_body = body_value 

    body = None;
    if raw_body:
        body = raw_body.strip().strip('"').replace('\\"', '"')  # allow quotes escaping inside JSON bodies.
        body = replace_env_variables(raw_body)  

    if g_debug:
        print(f"-> Processing request {testcase_id} for {request_url}")

    response, received_cookies, response_time_ms = send_https_request(
        not g_parse_only,
        http_method,
        request_url,
        request_headers,
        initial_cookies + request_cookies,
        args.use_configured_cookies,
        args.timeoutms,
        verify,
        args.client_cert,
        args.client_key,
        body
    )
    short_req_url = request_url.split("?")[0]
    #if not debug:
        #short_req_url = request_url[:40].ljust(34)
    status_code = None
    content_length = "0"
    if response is None:
        if isinstance(received_cookies, str):
            status_code = received_cookies; # ugly hack
    else:
        if response.headers.get('Content-Length'):
            content_length = response.headers.get('Content-Length')
        status_code = response.status_code
        resultstr = "FAIL";
        if not any(expected_statuses):
            resultstr = "UNKN";
        elif status_code in expected_statuses:
            resultstr = "PASS";
        testcase_results[testcase_id] = (short_req_url, resultstr, response.status_code, response_time_ms, content_length)
    print(f"-> {testcase_id}: {status_code}, {resultstr}, {response_time_ms:.2f} ms {content_length} {short_req_url} ..")
    time.sleep(delay_between_requests) # throttle the requests

    # process only count lines where possible.
    if g_num_tests > 0:
        g_num_tests = g_num_tests - 1;
        if g_num_tests == 0:
            break;

if g_stop_processing:
	print("Interrupted...\n");

print("\n\nSummary Report: -- ")
for testcase_id, (short_req_url, tcresult, status_code, time_ms, clen) in testcase_results.items():
    if status_code == "Timeout" or status_code == "SSLError":
        print(f"{testcase_id},  {status_code}, {tcresult}, {args.timeoutms:.2f}ms, {clen}, {short_req_url}")
    else:
        print(f"{testcase_id}, {status_code}, {tcresult}, {time_ms:.2f}ms, {clen}, {short_req_url}")
