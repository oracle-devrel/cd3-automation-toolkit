# OCI SDK Authentication Methods
Choose one of the below authentication mechansims to be used for the toolkit execution -

- [API key-based authentication](#api-key-based-authentication)
- [Session token-based authentication](#session-token-based-authentication)
- [Instance principal](#instance-principal)

## API key-based authentication
Follow below steps to use API key-based authentication - 
1. Create API PEM Key - RSA key pair in PEM format (minimum 2048 bits) is needed to use OCI APIs.
   <br>
   If the key pair does not exist, create them using below command inside docker container:
   <br>```cd /cd3user/oci_tools/cd3_automation_toolkit/user_scripts```
   <br>```python createAPIKey.py```
   <br>
→ This will generate the public/private key pair (oci_api_public.pem and oci_api_private.pem) at /cd3user/tenancies/keys/
   <br><br>
 In case you already have the keys, you can copy the private key file inside the container at /cd3user/tenancies/keys/

2. Upload Public Key
   <br>
   Upload the Public key to "APIkeys" under user settings in OCI Console. Pre-requisite to use the complete functionality of the Automation Toolkit is to have the user as an administrator to the tenancy.
      -  Open the Console, and sign in as the user.
      -  View the details for the user who will be calling the API with the key pair.
      -  Open the Profile menu (User menu icon) and click User Settings.
      -  Click Add Public Key.
      -  Paste the contents of the PEM public key in the dialog box and click Add.
  
   Required Details - user ocid and private key path
   
## Session token-based authentication
Follow below steps to use Session token-based authentication -


## Instance principal
