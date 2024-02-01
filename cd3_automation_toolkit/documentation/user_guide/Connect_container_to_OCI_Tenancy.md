# Connect container to OCI Tenancy

> [!Important]  
> * It is recommended to execute createTenancyConfig.py with a single <customer_name> within that container. Even if it is run multiple times with different customer names, Jenkins will only be configured for <customer_name> used while first time successful execution of the script.
> * If there is a new region subscription to the tenancy at a later stage of time, createTenancyConfig.py should be re-run by keeping the same details in tenancyconfig.properties(details like <customer_name>, <auth_mechanism> etc). It will just create a new directory for the new region under `/cd3user/tenancies/<customer_name>/terraform_files` and will keep the existing regions directories as is.

### **Step 1 - Exec into the Container**:
* Run  ```docker ps```.
<br> → Note down the container ID from this cmd output.
* Run  ```docker exec -it <container_id> bash```

### **Step 2 - Choose Authentication Mechanism for OCI SDK**</a>
* Please click [here](/cd3_automation_toolkit/documentation/user_guide/Auth_Mechanisms_in_OCI.md) to configure any one of the available authentication mechanisms.
  
### **Step 3 - Edit tenancyconfig.properties**:
* Run ```cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/```
* Fill the input parameters in **tenancyconfig.properties** file.
* Ensure to:
    -  Have the details ready for the Authentication mechanism you are planning to use.
    -  Use the same customer_name for a tenancy even if the script needs to be executed multiple times.
    -  Review **'outdir_structure_file'** parameter as per requirements. It is recommended to use seperate outdir structure to manage 
       a large number of resources. <br>
    -  Review Advanced Parameters Section for CI/CD setup and be ready with user details that will be used to connect to DevOps Repo in OCI.              Specifying these parameters as **'yes'** in properties file will create Object Storage Bucket and Devops Git Repo/Project/Topic in OCI 
       and enable toolkit usage via Jenkins.

 
### **Step 4 - Initialise the environment**:
* Initialise your environment to use the Automation Toolkit.
<br>```python createTenancyConfig.py tenancyconfig.properties```

> <b>Note</b>
> * If you are running docker container on a linux VM host, please refer to [point no. 7](/cd3_automation_toolkit/documentation/user_guide/FAQ.md) under FAQ to avoid any permission issues.
> * If the API Keys were generated and added to the OCI console using previous steps, it might take a couple of seconds to reflect. Thus, running the above command immediately might result in Authentication Errors. In such cases, please retry after a minute.
<br>

→ Example execution of the script with Advanced Parameters for CI/CD:

<img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/f8a6774a-da82-4d93-99b6-1bb4ae99fc37">


## Appendix

<details><summary><b> Expand this to view the details of the files created on successful execution of above steps </b></summary>

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
</details>
The next pages will guide you to use the toolkit either via CLI or via Jenkins. Please proceed further.
<br><br>


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
