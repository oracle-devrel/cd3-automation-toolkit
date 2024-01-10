# Connect Docker container to OCI Tenancy


> ***It is re***

### **Step 1 - Exec into the Container**:
* Run  ```docker ps```.
<br> → Note down the container ID from this cmd output.
* Run  ```docker exec -it <container_id> bash```

### <a href = "/cd3_automation_toolkit/documentation/user_guide/Auth_Mechanisms_in_OCI.md">**Step 2 - Choose Authentication Mechanism**</a>

### **Step 3 - Edit tenancyconfig.properties**:
* Fill the input parameters in **tenancyconfig.properties** file at /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/. 
* Please make sure you have the details ready for the authentication mechanism you have chosen. <br>
* Please make sure to use same customer_name for a tenancy even if the script needs to be executed multiple times.
* Please make sure to review 'outdir_structure_file' parameter as per requirements. It is recommended to use seperate outdir structure in case the tenancy has large number of objects. <br>
* Please make sure to review Advanced Parameters Section for CI/CD setup and be ready with user details that will be used to connect to DevOps Repo in OCI.
```
[Default]

##################################################################################################################
                            ## Required Parameters ##
##################################################################################################################

# Friendly name for the Customer Tenancy eg: demotenancy; The generated .auto.tfvars files will be prefixed with this
# customer_name.
customer_name=

tenancy_ocid=

# Example: us-phoenix-1
region=

# Auth Mechanism for OCI APIs - api_key,instance_principal,session_token
# Please make sure to add IAM policies for user/instance_principal before executing createTenancyConfig.py
auth_mechanism=api_key

##################################################################################################################
                            ## Auth Details Parameters ##
# Required only for ${auth_mechanism} as api_key; Leave below params empty if 'instance_principal' or 'session_token'
# is used
##################################################################################################################

user_ocid=
#Path of API Private Key (PEM Key) File; Defaults to /cd3user/tenancies/keys/oci_api_private.pem when left empty
key_path=
fingerprint=

##################################################################################################################
                            ## Deployment Parameters ##
##################################################################################################################

# The outdir_structure_file defines the grouping of the terraform auto.tf.vars for the various generated resources.
# To have all the files generated in a single directory in the corresponding region, leave this variable blank.
# To group resources into different directories within each region - specify the absolute path to the file.
# The default file is specified below. You can make changes to the grouping in the below file to suit your deployment
#outdir_structure_file=
#or
outdir_structure_file=/cd3user/oci_tools/cd3_automation_toolkit/user-scripts/outdir_structure_file.properties

# SSH Key for launched instances; Use '\n' as the delimiter to add multiple ssh keys.
# Example: "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
# Optional
ssh_public_key=

##################################################################################################################
                            ## Advanced Parameters for DevOps ##
# Needed for Jenkins Configuration
# Below OCI Objects - Remote State Bucket Name and DevOps Project/Repo and a Notification Topic will be created/fetched
# from region specified in ${region} above.
##################################################################################################################


# Compartment OCID where Bucket and DevOps Project/repo will be created; defaults to root if left empty.
compartment_ocid=

# Remote state configuration
# Enter yes if remote state needs to be configured, else tfstate will be stored on local filesystem.
use_remote_state=no

# If left empty then Bucket with name ${customer_name}-tfstate-bucket will be created/reused in ${region}.
remote_state_bucket_name=

# OCI DevOps GIT configuration
# Enter yes if generated terraform_files need to be stored in OCI DevOps GIT Repo else they will be stored on local
# filesystem. Will enforce 'yes' for use_remote_state in case below is set to 'yes'
use_oci_devops_git=no

# If left empty then DevOps items  with names ${customer_name}-automation-toolkit-project/repo/topic will be created/reused
# in ${region}.
# Format: <project_name/repo_name>
oci_devops_git_repo_name=

# User Details to perform GIT operations in OCI Devops GIT Repo; Mandatory when using $(auth_mechanism) as instance_principal
# or session_token
# Format: <domainName>/<userName>@<tenancyName> Refer to 'Setting up SSH Authentication' under
# https://docs.oracle.com/en-us/iaas/Content/devops/using/ssh_auth.htm
# When left empty, it will be fetched from $(user_ocid) for $(auth_mechanism) as api_key.
# Customer Secret Key will also be configured for this user for S3 credentials of the bucket when $(auth_mechanism) is
# instance_principal or session_token
oci_devops_git_user=
# When left empty, same key file from $(key_path) used for $(auth_mechanism) as api_key will be copied to
# /cd3user/tenancies/<customer_name>/ and used for GIT Operations.
oci_devops_git_key=
```
### **Step 5 - Initialise the environment**:
Initialise your environment to use the Automation Toolkit.
<br>```python createTenancyConfig.py tenancyconfig.properties```

**Note** - If the API Keys were generated and added to the OCI console using previous steps, it might take a couple of seconds to reflect. Thus, running the above command immediately might result in Authentication Errors.<br>In such cases, please retry after a minute.
<br>

→ Example execution of the script with Advanced Parameters for CI/CD:

<img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/7f7cfce9-51ad-4510-9c86-c85b51cd90a6">




## Appendix
→ Files created on successful execution of above steps - Description of the Generated files:

| Files Generated | At File Path | Comment/Purpose |
| --------------- | ------------ | --------------- |
| Config File | ```/cd3user/tenancies/<customer_name>/<customer_name>_config``` | Customer specific Config file is required for OCI API calls. This will have data based on authentication mechanism chosen. |
| setUpOCI.properties | ```/cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties``` | Customer Specific properties files will be created. |
| outdir_structure_file.properties | ```/cd3user/tenancies/<customer_name>/<customer_name>_outdir_structure_file``` | Customer Specific properties file for outdir structure.<br> This file will not be generated if 'outdir_structure_file' parameter was set to empty(single outdir) in tenancyconfig.properties while running createTenancy.py |
| Region based directories | ```/cd3user/tenancies/<customer_name>/terraform_files``` | Tenancy's subscribed regions based directories for the generation of terraform files.<br>Each region directory will contain individual directory for each service based on the parameter 'outdir_structure_file' |
| Variables File,Provider File, Root and Sub terraform modules | ```/cd3user/tenancies/<customer_name>/terraform_files/<region>``` | Required for terraform to work. Variables file and Provider file will be genrated based on authentication mechanism chosen.|
| GIT Config File | ```/cd3user/tenancies/<customer_name>/<customer_name>_git_config``` | Customer specific GIT Config file for OCI Dev Ops GIT operations |
| S3 Credentials File | ```/cd3user/tenancies/<customer_name>/<customer_name>_s3_credentials``` | This file contains access key and secret for S3 compatible OS bucket to manage remote terraform state. |
| Public and Private Key Pair | Copied from ```/cd3user/tenancies/keys/```<br>to<br>```/cd3user/tenancies/<customer_name>/``` | API Key for authentication mechanism as API_Key are moved to customer specific out directory locations for easy access. |
| Jenkins Home | ```/cd3user/tenancies/jenkins_home``` | This folder contains jenkins specific data. Single Jenkins instance can be setup for a single container. |
| out file | ```/cd3user/tenancies/<customer_name>/createTenancyConfig.out``` | This file contains a copy of information displayed as the console output. |


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
