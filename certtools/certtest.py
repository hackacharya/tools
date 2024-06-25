#!/usr/bin/env python3

#
# ./certs.sh createca devca1
#
# ./certs.sh genkey mywebapp25
# ./certs.sh gencsr mywebapp25
#
# ./certs.sh issuecert mywebapp25
# ./certs.sh showcert mywebapp25
#
# ./certtest.py app25
#
#

import ssl
import sys

svc=sys.argv[1]
certfile=svc+'.crt'
keyfile=svs+'.key'

#ca=sys.argv[2]
#cachain="ca/"+ca+".crt"

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#ssl_context.load_verify_locations(cafile);
ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
print("Loaded certs successfully!");
