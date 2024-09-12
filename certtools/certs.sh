#!/bin/bash
#
#
# Sigh how many times do folks have to write this
# for folks starting with certs, and learning 
# TLS, mTLS
#
# Get this out there. srini@hackacharya.com
#
# WARNING!! NOT the best practices!
# WARNING!! This is a learning tool dont use for
# production 
#
#   Things that you should really be doing.
#   RSA keys use aes256 encryption 
#   Use atleast 2048 bits 
#   Use a proper serial number DB  
#
#
# Call from the same directory, dont call with a path, it wont
# find the files. 
#
# https://www.openssl.org/docs/man1.1.1/man1/
#

case $1 in 

                   ############# ca stuff #########
createca)
   mkdir -p ./ca
   CA=$2
   echo "Creating new Cert Authority $CA valid for 10 years ... " ;
   echo
   echo "** Enter a nice domain/hostname/appname/svcname in the CN field **"
   echo 
   openssl genrsa -out ca/${CA}_CA.key 2048
   chmod go-rwx ca/${CA}_CA.key
   openssl req -x509 -new -key ca/${CA}_CA.key -sha256 -days 3650 -out ca/${CA}_CA.crt 
   openssl rsa -in ca/${CA}_CA.key -pubout > ca/${CA}_CA.pub
   echo "CA key ca/${CA}_CA.key, Cert=ca/${CA}_CA.crt" 
   ;;

createaesca)
   mkdir -p ./ca
   CA=$2
   echo "Creating new Cert Authority $CA valid for 10 years ... " ;
   echo
   openssl genrsa -out ca/${CA}_CA.key 2048
   chmod go-rwx ca/${CA}_CA.key
   openssl req -x509 -new -key ca/${CA}_CA.key -sha256 -days 3650 -out ca/${CA}_CA.crt 
   openssl rsa -in ca/${CA}_CA.key -pubout > ca/${CA}_CA.pub
   echo "CA key ca/${CA}_CA.key, ca/Cert=${CA}_CA.crt"
   ;;

issuecert)
  CA=$2
  APP=$3
  echo "Trying to issue a certificate from ${APP}.csr CSR using ${CA} valid for 1 year .."
  echo
  # openssl x509 -req -days 365 -in ${APP}.csr  -signkey ca/${CA}_CA.key  -out ${APP}.crt
  openssl x509 -req -days 365 -in ${APP}.csr -CA ca/${CA}_CA.crt -CAkey ca/${CA}_CA.key -out ${APP}.crt
  echo "Your signed cert should be in ${APP}.crt.."
  ;;

issuesancert)
  CA=$2
  APP=$3
  echo "Trying to issue a certficate based on CSR ${APP}.csr using ${CA} valid for 1 year .."
  echo
  cat > extension.${APP} << END_OF_EXT
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = ${APP}
END_OF_EXT
  openssl x509 -req -in ${APP}.csr -CA ca/${CA}_CA.crt -CAkey ca/${CA}_CA.key \
	-CAcreateserial -out ${APP}.crt -days 365 -sha256 -extfile extension.${APP}
  ;;

                     ############# app stuff #########

genaeskey)
   APP=$2;
   echo "Generating a new password protected key pair for an app ${APP}"
   # Warning we are not using AES
   openssl genrsa -aes256 -out ${APP}.key 2048
   openssl rsa -in ${APP}.key -pubout > ${APP}.pub
   chmod go-rwx ${APP}.key
   ;;

genkey)
   APP=$2;
   echo "Generating a new key pair for an app ${APP}"
   # Warning we are not using AES
   openssl genrsa -out ${APP}.key 2048
   openssl rsa -in ${APP}.key -pubout > ${APP}.pub
   chmod go-rwx ${APP}.key
   ;;

gencsr)
    APP=$2;
    echo "Generating a Certificate signing request for a $APP"
    echo 
    echo "** Enter your domain/hostname/appname/svcname in the CN field **"
    echo
    openssl req -new -key ${APP}.key -out ${APP}.csr
    ;;

showcacert)
    CA=$2;
    openssl x509 -in ca/${CA}_CA.crt -text 
    ;;

showcert)
    APP=$2;
    openssl x509 -in ${APP}.crt -text 
    ;;

showfingerprint)
    APP=$2
    echo "SHA256 finger print for ${APP} cert .."
    openssl x509 -noout -fingerprint -sha256 -inform pem -in ${APP}.crt 
    ;;

runserver)
    APP=$2;
    PORT=$3;
    echo "Starting server for ${APP} with its key and certs on ${PORT}... "
    openssl s_server -key ${APP}.key -cert ${APP}.crt -accept ${PORT}
    ;;

runserverwithca)
    APP=$2;
    PORT=$3;
    CA=$3
    echo "Starting server for ${APP} with its key and certs on ${PORT} trusting ${CA}... "
    openssl s_server -key ${APP}.key -cert ${APP}.crt -CAfile ca/${CA}_CA.crt -accept ${PORT}
    ;;

runclient)
    APP=$2;
    HOST=$3;
    PORT=$4;
    echo "Starting client with ${APP} certs to connect to ${HOST}:${PORT}..."
    openssl s_client -connect ${HOST}:${PORT} -servername ${HOST} \
	-key ${APP}.key -cert ${APP}.crt -showcerts -debug
    ;;

runclientwithca)
    APP=$2;
    HOST=$3;
    PORT=$4;
    echo "Starting client with ${APP} certs to connect to ${HOST}:${PORT}..."
    openssl s_client -connect ${HOST}:${PORT} -servername ${HOST} -key ${APP}.key -cert ${APP}.crt 
    ;;

compare)
    APP=$2;
    echo "Key"
    openssl rsa -noout -modulus -in ${APP}.key
    echo "CSR"
    openssl x509 -noout -modulus -in ${APP}.crt
    echo "Cert"
    openssl x509 -noout -modulus -in ${APP}.csr
    ;;

#trustCA)
   #CA=$2
   #cp ca/{CA}_CA.pub /usr/local/share/ca-certificates/{$yCA.crt
   #update-ca-certificates 
   #;;

help|*)
  cat << END_OF_HELP
  Dev/Test Certificate Generation, Signing help tool

  CA operations
   createca <caname> - Creates a CA 
   issucert <caname> <appname>  - Using the given CA and a CSR generated 
                                  for an svc/app - issue a cert to the app 
   issusancert <caname> <appname> - Using the given CA and a CSR generated 
                                    for an svc/app - issue a cert to the app 
			             this cert will contain SAN also
				   Now a days you need SAN in addition to CN
   showcacert <ca>   - show the cert file name for the app or the ca

  App operations
   genkey <appname>  - Generates a new Key pair for an app/service
   gencsr <appname>  - Using the key generated earlier generates a Cert Sign REqeust

  Test operations
   showcert <cappname> - show the cert file name for the app or the ca
   showfingerprint  <appname> - show the cert file SHA256 finger print 
   compare <appname> - Check if the pubkey is the same in all keys/certs.
   runclient <appname> <host> <portnum>
   runclientwithca <appname> <host> <portnum> <caname>
   runserver <appname> <portnum>
   runserverwithca <appname> <portnum> <caname>
    

    Example Usage

    Once 
      1. Create a CA  - ./certs.sh createca DevCA 

    For each svc/app that needs a cert
      2. Create a key for an svc mywebserver.local  
		 ./certs.sh genkey mywebserver.local
      3. Create a CSR for an svc mywebserver.local  
		 ./certs.sh gencsr mywebserver.local
      4. Issue a certificate for that local using the benerated CSR , using the Dev CA
		./certs.sh issuesancert DevCA mywebserver.local
      4. SHow an app cert  in text
		./certs.sh showcert mywebserver.local

END_OF_HELP
   ;; 

esac


# End
