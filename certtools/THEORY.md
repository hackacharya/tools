

 Notes For Rookies!

 WARNING!! not exactly according to TLS protocol 
 But a high level view of what happens. 

 Note this is not regular 'web' - while most of it
 apply to how browsers work.

 Regular TLS Server verification done at client isde

  client ----> server (xyz.com, myserver)

 1. Client does DNS lookup for xyz.com, or myserver or myweba/pp etc
	Note these are not always 'internet' conenctions remember
 2. Client makes a TCP connection to IP adddress and port
 3. Now the TLS work begins 
 4a. (mTLS) The client may send the certificate it has one configured
     It may also send the signing CAs cert along with the reqeust
	| client-cert
	| CN=user@example.org 
        | Expriy: In 2 years.
	| Issuer: MIcrosoft CA
        or if it is internal  ...
	.| client-cert
	| CN=myclientapp 
        | Expriy: In 2 years.
	| Issuer: Unknown Internal CA
 4b. (mTLS) The server checks if the client is sending a valid cert
	If it likes everything about the cert, the name, expiry
        and the issuer, it will proceed.
	The server operating system has a lsit of trusted CAS
	here if it finds Microsoft CA it will let the conenction ghrough
	It may also check the "CN" for valid users/apps. These are
	usually configured on the server.
	If it doesn't like the CA, then the server must be told
	to trust the CA (so the certificate of the CA that issued
	the client certificate is configured on the Server, to 
	ensure it can allow connection).
 4. Client asks to see the server cert.
 5a. Case a) Server sends its  certficate that contains info like this
	| cert
	| CN=xyz.com
	| SAN=xyz.com,service1.xyz.com 
        | Expriy: In 2 years.
	| Issuer: Verisign CA
 5a. Case b) Server may send a certificate issued internally by 
	a non-wellknown/trusted CA 
	| cert
	| CN=servicename
	| SAN=servicename,othernames
        | Expriy: in 30 days
	| Issuer: Unknown Self CA
 6. Client checks who issued the certificate 
	case a) The client operating system usually has a list of trusted CAs
	In this case the versign cverticiate authority has signed 
	So good client proceeds.
	case b) The client is 'loaded' with other trusted CAs when it made
        the connection. 'Unknown Self CA' certificate is given to the client
	at the time of initalization of the TLS connection - client is now
	happy and it will also accept 'Unknown Self CA' issued certificates
 7. Client checks if the CN/SAN have the 'exact' hostname/fqdn
    that it was trying to connect to 
    IN this case the CN/SAN are good so it has 'verified' 
    that it is connect to the right server

 8. Client chekcs if the certificate is VALID (expiry is good)

 9. Client ensures if the certificate is not revoked, by chedcking aginst
    revocation lists (oscp)


 Some psuedo code may look like this  on the client side
	url='https://service:8993/path"
	requests.get(URL, ssl_ca_cert_chain="ca/certchain.pem")

  If the client wishes to send its client cert for authentication  (MTLS) client cert auth
	url='https://service:8993/path"
	requests.get(URL, cert="app.crt", key="app.key", ssl_ca_cert_chain="ca/certchain.pem")



