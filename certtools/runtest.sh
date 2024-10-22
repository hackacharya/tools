#!/usr/bin/env bash

case $1 in 
cleanup) rm -fr extension.* *.key *.crt *.pub *.csr ./ca ; echo "Cleaned up." ; exit 0;;
esac 

./certs.sh createca devca1 blanks

./certs.sh genkey mywebapp25
./certs.sh gencsr mywebapp25 blanks
./certs.sh issuesancert devca1 mywebapp25 mywebapp25.namespace mywebapp25.namespace.svc mywebapp25.namespace.svc.cluster.local
./certs.sh showcert mywebapp25
#./certtest.py mywebapp25
