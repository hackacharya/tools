  #Dev/Test Certificate Generation, Signing help tool

  #CA operations
   createca <caname> - Creates a CA 
   
   issucert <caname> <appname>  - Using the given CA and a CSR generated 
                                  for an svc/app - issue a cert to the app 
				  
   issusancert <caname> <appname> - Using the given CA and a CSR generated 
                                    for an svc/app - issue a cert to the app 
			             this cert will contain SAN also
				   Now a days you need SAN in addition to CN
       
   showcacert <ca>   - show the cert file name for the app or the ca

  #App operations
   genkey <appname>  - Generates a new Key pair for an app/service
   
   gencsr <appname>  - Using the key generated earlier generates a Cert Sign REqeust

  #Test operations
   showcert <cappname> - show the cert file name for the app or the ca
   
   showfingerprint  <appname> - show the cert file SHA256 finger print 
   
   compare <appname> - Check if the pubkey is the same in all keys/certs.
   
   runclient <appname> <host> <portnum>
   
   runclientwithca <appname> <host> <portnum> <caname>
   
   runserver <appname> <portnum>
   
   runserverwithca <appname> <portnum> <caname>

    

   #Example Usage

    Once  - you would do this once generally (unless you want several CAs)
      1. Create a CA  - ./certs.sh createca DevCA 

    For each svc/app that needs a cert (the name you give here goes into the CN / Subject and SAN)

      2. Create a key for an svc mywebserver.local  
		 ./certs.sh genkey mywebserver.local
      3. Create a CSR for an svc mywebserver.local  
		 ./certs.sh gencsr mywebserver.local
      4. Issue a certificate for that local using the benerated CSR , using the Dev CA
		./certs.sh issuesancert DevCA mywebserver.local
      4. SHow an app cert  in text
		./certs.sh showcert mywebserver.local

