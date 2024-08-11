
INJECTOR QUICK START

1. Make a copy of the csv file
2. Put in your URLs, headers
3. If you have login - manually do the login , copy over the cookies.
3. Run the tool 
	--debug for more detailed messaging.

To get the cookies.json
  use Firefox or any browser, go into dev mode, look at the request and Find the cookies header and doa "COPY all" and paste into this cookies.json file.
  The format is the firefox export format.



Example request-details file

Testcase ID,HTTP Method,URL,Headers,Cookies,Body
TC001,GET,http://api.example.org/,,,,
TC002,POST,/api/v1/search,"Content-Type=application/json,Authorization=Bearer abc123,X-Custom-Header=value","session_id=abc123, user_id=xyz456","{user_id:joe}"
TC003,PUT,/api/savedetails,"Content-Type=application/text,Authorization=Bearer abc123",,user_id=123
TC005,PUT,/api/savedetails,"Content-Type=application/text,Authorization=Bearer ${API_TOKEN}"
TC005,POST,/api/createobject,"Content-Type=application/text,Authorization=Bearer ${API_TOKEN}",,"{obj_name:one}"
TC006,POST,https://api.example.org/api/createobject,"Content-Type=application/text,Authorization=Bearer ${API_TOKEN}",,@TC006.data

# Escape commas(,) and is-equal-to signs (=) in header values with a backslash.
# Multiple headers with both , and = embedded in the values
#  = "Accept=text/html\,application/xhtml+xml\,application/xml;q\=0.9;image/avif\,image/webp\,image/png\,image/svg+xml\,*/*;q\=0.8,Content-Type=application/json"
