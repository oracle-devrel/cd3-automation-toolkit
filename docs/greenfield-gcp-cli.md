# **Create and Manage Resources in GCP (Greenfield Workflow)**
---


<span style="color: teal; font-weight: bold;">Step 1:</span>

Choose the excel sheet template from <a href="../gcp-excel-templates"><u>Excel Templates</u></a>.
Fill the Excel with appropriate values and copy at `/cd3user/gcp/<prefix>`<br>

<b>Copy CD3 Excel File</b><br>

* While using the container launched using <a href="../launch-from-rmstack"><u>RM Stack</u></a>, local path `/cd3user/mount_path` on the VM is mapped to `/cd3user/` inside the container. So the Excel template can be copied at `/cd3user/mount_path/gcp/<prefix>/` on the VM. Below is the sample command to copy the Excel template from local system to container:
```
scp -i <private key pushed to VM while creating stack> <path to excel file on local> cd3user@<Public/Private IP of the VM>:/cd3user/mount_path/gcp/<prefix>
``` 

* Note that the user `cd3user` can be used to connect to the VM because same key is pushed for `opc` as well as `cd3user`.

<span style="color: teal; font-weight: bold;">Step 2:</span>

Modify ```/cd3user/gcp/<prefix>/<prefix>_setUpGCP.properties```.
<br>Update parameters: **cd3file** parameter to the location of CD3 excel file and  **workflow_type**  to **create_resources** as shown below.
<br> The other parameters are already updated with correct values.
```ini

[Default]

#Input variables required to run setUpGCP script

#path to output directory where terraform files will be generated. eg. /cd3user/gcp/<prefix>/terraform_files
outdir=

#prefix for output terraform files eg demo
prefix=

# Auth Params
# auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=api_key

#input credentials file for service account eg /cd3user/gcp/<prefix>/gcp_api_private.pem
config_file=

#path to cd3 excel eg /cd3user/gcp/<prefix>/CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in GCP(greenfield workflow)
#specify export_resources to export resources from GCP(non-greenfield workflow)
workflow_type=create_resources

```

<span style="color: teal; font-weight: bold;">Step 3:</span>

Execute the setUpCloud.py script to start creating the terraform configuration files.
    
Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```
```
python setUpCloud.py gcp /cd3user/gcp/<prefix>/<prefix>_setUpGCP.properties
```
         
!!! example "Example Execution"

    [cd3user@dc6dac212f79 cd3_automation_toolkit]$ python setUpCloud.py gcp /cd3user/gcp/gcp_demo/gcp_demo_setUpGCP.properties 

    Choose appropriate option from below :

    1. Create DB@GCP
    <br>q. Press q to quit

    See example folder for sample input files
 
    Enter your choice (specify comma separated to choose multiple choices): 


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.<br>



<span style="color: teal; font-weight: bold;">Expected Outputs:</span>

The tfvars files for the selected services will be generated at the following path:
`/cd3user/gcp/<prefix>/terraform_files/`


<span style="color: teal; font-weight: bold;">Step 4:</span>

Change the directory to  ```/cd3user/gcp/<prefix>/terraform_files/``` 

  - Execute:


    ```terraform init```  - *To initialize and prepare the working/out directory so Terraform can run the configuration*<br>

    ```terraform plan```  - *To preview any changes before applying them*<br>

    ```terraform apply``` - *To make the changes defined by Terraform configuration to create, update, or destroy resources in GCP*

