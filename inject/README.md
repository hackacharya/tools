
INJECTOR QUICK START 1.5

1. Make a copy of the csv file
2. Put in your URLs, headers
3. If you have login - manually do the login , copy over the cookies.
3. Run the tool 
	--debug for more detailed messaging.

To get the cookies.json
  use Firefox or any browser, go into dev mode, look at the request and Find the cookies header and doa "COPY all" and paste into this cookies.json file.
  The format is the firefox export format.

REserved patterns
 $kMa$
 $esCol$

CSV Header and Keys.
Testcase ID,HTTP Method,Expected Statuses,URL,Headers,Cookies,Body

Expeted Statuses column can have multiple values '|' seperated like
  400|200|300 
  0 status is treated as UKNN result.

Example request-details file

Testcase ID,HTTP Method,Expected Statuses,URL,Headers,Cookies,Body
TC001,GET,http://api.example.org/,,,,
TC002,POST,200,/api/v1/search,"Content-Type:application/json,Accept:text/plain,X-Custom-Header:value","session_id=abc123, user_id=xyz456","{user_id:joe}"
TC003,PUT,200,/api/savedetails,"Content-Type:text/plain,Accept: */*",,user_id=123
TC005,PUT,000,/api/savedetails,"Content-Type:text/plain,Authorization:Bearer ${API_TOKEN}",,blah
TC005,POST,200|202,/api/createobject,"Content-Type=application/json,Authorization=Bearer ${API_TOKEN}",,{"obj_name":"one"${kMA} "obj_type": "blah"}
TC006,POST,403|404,https://api.example.org/api/createobject,"Content-Type=application/json,Authorization=Bearer ${API_TOKEN}",,@TC006-file.data

#  "Accept:text/html\,application/xhtml+xml\,application/xml;q=0.9;image/avif\,image/webp\,image/png\,image/svg+xml\,*/*;q=0.8,Content-Type:application/json"
# For JSON bodies use ${kMA} for commas or use files '@filename'
TC006,POST,500,https://api.example.org/api/createobject,"Content-Type:application/text,Authorization:Bearer ${API_TOKEN}",,{"name":"value"${kMa}, "another field":"another value"}
