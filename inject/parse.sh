#/bin/sh

API_TOKEN="injectortoken838384abceeff"
export API_TOKEN
./injector.py --url-prefix https://api.example.org  --request-details-csv request-details.csv  --show-cookies --cookie-file cookies.json --debug --parse-only
