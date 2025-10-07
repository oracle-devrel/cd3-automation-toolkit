# **Create and Manage Resources in Azure (Greenfield Workflow)**
---


<span style="color: teal; font-weight: bold;">Step 1:</span>

Choose the excel sheet template from <a href="../azr-excel-templates"><u>Excel Templates</u></a>.
Fill the Excel with appropriate values and copy at `/cd3user/azure/<prefix>`<br>

<span style="color: teal; font-weight: bold;">Step 2:</span>

Modify ```/cd3user/azure /<prefix>/<prefix>_setUpAzure.properties```.
<br>Update parameters: **cd3file** parameter to the location of CD3 excel file and  **workflow_type**  to **create_resources** as shown below.
<br> The other parameters are already updated with correct values.
```ini
[Default]

#Input variables required to run setUpAzure script

#path to output directory where terraform file will be generated. eg /cd3user/azure/<prefix>/terraform_files
outdir=

#prefix for output terraform files eg demo
prefix=

# Auth Params
subscription_id=

tenant_id=

client_id=

client_secret=

#path to cd3 excel eg /cd3user/azure/<prefix>\CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in Azure(greenfield workflow)
#specify export_resources to export resources from Azure(non-greenfield workflow)
workflow_type=create_resources
```


<span style="color: teal; font-weight: bold;">Step 3:</span>

Execute the setUpCloud.py script to start creating the terraform configuration files.
    
Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```
```
python setUpCloud.py azure /cd3user/azure/<prefix>/<prefix>_setUpAzure.properties
```
         
!!! example "Example Execution"

    [cd3user@dc6dac212f79 cd3_automation_toolkit]$ python setUpCloud.py azure /cd3user/azure/az_demo/az_demo_setUpAzure.properties 

    Choose appropriate option from below :

    1. Create DB @Azure
    <br>q. Press q to quit

    See example folder for sample input files
 
    Enter your choice (specify comma separated to choose multiple choices): 


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.<br>



<span style="color: teal; font-weight: bold;">Expected Outputs:</span>

The tfvars files for the selected services will be generated at the following path:
`/cd3user/azure/<prefix>/terraform_files/`


<span style="color: teal; font-weight: bold;">Step 4:</span>

Change the directory to  ```/cd3user/axure/<prefix>/terraform_files/``` .

  - Execute:


    ```terraform init```  - *To initialize and prepare the working/out directory so Terraform can run the configuration.*<br>

    ```terraform plan```  - *To preview any changes before applying them. *

    ```terraform apply``` - *To make the changes defined by Terraform configuration to create, update, or destroy resources in Azure.*

   S