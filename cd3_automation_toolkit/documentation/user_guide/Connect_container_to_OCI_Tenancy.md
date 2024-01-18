# Connect Docker container to OCI Tenancy


> ***It is suggested to create a dedicated container for a single tenancy.***

### **Step 1 - Exec into the Container**:
* Run  ```docker ps```.
<br> → Note down the container ID from this cmd output.
* Run  ```docker exec -it <container_id> bash```

### **Step 2 - Choose Authentication Mechanism for OCI SDK**</a>
* Please click [here](/cd3_automation_toolkit/documentation/user_guide/Auth_Mechanisms_in_OCI.md) to configure any one of the available authentication mechanisms.
  
### **Step 3 - Edit tenancyconfig.properties**:
* Run ```cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/```
* Fill the input parameters in **tenancyconfig.properties** file. 
* Please make sure you have the details ready for the authentication mechanism you have chosen. <br>
* Please make sure to use same customer_name for a tenancy even if the script needs to be executed multiple times.
* Please make sure to review 'outdir_structure_file' parameter as per requirements. It is recommended to use seperate outdir structure in case the tenancy has large number of objects. <br>
* Please make sure to review Advanced Parameters Section for CI/CD setup and be ready with user details that will be used to connect to DevOps Repo in OCI.
 
### **Step 4 - Initialise the environment**:
* Initialise your environment to use the Automation Toolkit.
<br>```python createTenancyConfig.py tenancyconfig.properties```

> <b>Note</b>
> * If you are running docker container on a linux VM host, please look at [this](/cd3_automation_toolkit/documentation/user_guide/FAQ.md) under FAQ to avoid any permission issues.
> * If the API Keys were generated and added to the OCI console using previous steps, it might take a couple of seconds to reflect. Thus, running the above command immediately might result in Authentication Errors. In such cases, please retry after a minute.
<br>

→ Example execution of the script with Advanced Parameters for CI/CD:

<img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/7f7cfce9-51ad-4510-9c86-c85b51cd90a6">




## Appendix
→ Files created on successful execution of above steps - Description of the Generated files:

| Files Generated | At File Path | Comment/Purpose |
| --------------- | ------------ | --------------- |
| setUpOCI.properties | ```/cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties``` | Customer Specific properties |
| outdir_structure_file.properties | ```/cd3user/tenancies/<customer_name>/<customer_name>_outdir_structure_file``` | Customer Specific properties file for outdir structure.<br> This file will not be generated if 'outdir_structure_file' parameter was set to empty(single outdir) in tenancyconfig.properties while running createTenancyConfig.py |
| Region based directories | ```/cd3user/tenancies/<customer_name>/terraform_files``` | Tenancy's subscribed regions based directories for the generation of terraform files.<br>Each region directory will contain individual directory for each service based on the parameter 'outdir_structure_file' |
| Variables File,Provider File, Root and Sub terraform modules | ```/cd3user/tenancies/<customer_name>/terraform_files/<region>``` | Required for terraform to work. Variables file and Provider file will be genrated based on authentication mechanism chosen.|
| out file | ```/cd3user/tenancies/<customer_name>/createTenancyConfig.out``` | This file contains a copy of information displayed as the console output. |
| OCI Config File | ```/cd3user/tenancies/<customer_name>/.config_files/<customer_name>_oci_config``` | Customer specific Config file for OCI API calls. This will have data based on authentication mechanism chosen. |
| Public and Private Key Pair | Copied from ```/cd3user/tenancies/keys/```<br>to<br>```/cd3user/tenancies/<customer_name>/.config_files``` | API Key for authentication mechanism as API_Key are copied to customer specific out directory locations for easy access. |
| GIT Config File | ```/cd3user/tenancies/<customer_name>/.config_files/<customer_name>_git_config``` | Customer specific GIT Config file for OCI Dev Ops GIT operations. This is generated only if use_oci_devops_git is set to yes |
| S3 Credentials File | ```/cd3user/tenancies/<customer_name>/.config_files/<customer_name>_s3_credentials``` | This file contains access key and secret for S3 compatible OS bucket to manage remote terraform state. This is generated only if use_remote_state is set to yes |
| Jenkins Home | ```/cd3user/tenancies/jenkins_home``` | This folder contains jenkins specific data. ```Single Jenkins instance can be setup for a single container.```|


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
