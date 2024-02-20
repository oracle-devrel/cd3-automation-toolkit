# OCI SDK Authentication Methods
Choose one of the below authentication mechanisms to be used for the toolkit execution -

- [API key-based authentication](#api-key-based-authentication)
- [Session token-based authentication](#session-token-based-authentication)
- [Instance principal](#instance-principal)

## API key-based authentication
Follow below steps to use API key-based authentication - 
1. Create API PEM Key - RSA key pair in PEM format (minimum 2048 bits) is needed to use OCI APIs.
   <br>
   If the key pair does not exist, create them using below command inside docker container:
   <br>```cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/```
   <br>```python createAPIKey.py```
   <br>
→ This will generate the public/private key pair (oci_api_public.pem and oci_api_private.pem) at /cd3user/tenancies/keys/
   <br><br>
 In case you already have the keys, you can copy the private key file inside the container at /cd3user/tenancies/keys/

2. Upload Public Key
   <br>
   Upload the Public key to "APIkeys" under user settings in OCI Console.
      -  Open the Console, and sign in as the user.
      -  View the details for the user who will be calling the API with the key pair.
      -  Open the Profile menu (User menu icon) and click User Settings.
      -  Click Add Public Key.
      -  Paste the contents of the PEM public key in the dialog box and click Add.
  
   > <b>Note</b>
   > * Please note down these details for next step - User OCID, Private Key path, Fingerprint, Tenancy OCID. The User should have administrator access to the tenancy to use complete functionality of the toolkit.
   
## Session token-based authentication
Follow below steps to use Session token-based authentication - 
1. Use below command to create config inside the container. This is needed to generate session token. You can skip this step, if you already have a valid config(with API key) and uploaded the public key to OCI for a user. In that case, you can copy the config file and private API Key inside the container at /cd3user/.oci
   <br>```oci setup config```

      <img width="509" alt="Screenshot 2024-01-04 at 4 43 08 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/d97b6407-8032-40a3-a5d1-98778be867af">
      
2. Execute ```oci session authenticate --no-browser``` to generate session token for the private key.
   <br> Follow the questions. Enter 'DEFAULT' for the profile name and proceed to update the config file with session token information at default location /cd3user/.oci
 
   <img width="721" alt="Screenshot 2024-01-04 at 4 49 53 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/3f65e41c-971f-4e17-8e23-a839317d8912">
3. Token will be generated at default location /cd3user/.oci     

   <img width="512" alt="Screenshot 2024-01-04 at 4 55 17 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/0b3446f6-b69a-49cd-858a-7a14380c4552">

> <b>Note</b>
> * createTenancyConfig.py script will use the config file located at /cd3user/.oci path. And toolkit supports profile name as DEFAULT only.
> * Generated session token will have maximum 60 minutes validity. You will have to follow from step 1 if new session token is required after expiry. The User should have administrator access to the tenancy to use complete functionality of the toolkit.

## Instance principal
Follow below steps to use Instance Principal authentication - 
1. Launch and Instance in the tenancy and set up the toolkit docker container on that instance.
2. Create Dynamic Group for this instance.
3. Write IAM policy to assign privileges to this dynamic group. The dynamic group(containing the instance) should have administrator access to the tenancy to use complete functionality of the toolkit.


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md#step-1---exec-into-the-container">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md#step-3---edit-tenancyconfigproperties">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
