# **Create and Manage Resources in OCI (Greenfield Workflow)**
---


<span style="color: teal; font-weight: bold;">Step 1:</span>

Choose the appropriate excel sheet template from <a href="../excel-templates"><u>Excel Templates</u></a>.
Fill the Excel with appropriate values and copy at `/cd3user/tenancies/<prefix>`<br>

<span style="color: teal; font-weight: bold;">Step 2:</span>

Modify ```/cd3user/tenancies /<prefix>/<prefix>_setUpOCI.properties```.
<br>Update parameters: **cd3file** parameter to the location of CD3 excel file and  **workflow_type**  to **create_resources** as shown below.
<br> The other parameters are already updated with correct values.
```ini
#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<prefix>/terraform_files
outdir=/cd3user/tenancies/demo/terraform_files/

#prefix for output terraform files eg <customer_name> like demo
prefix=demo

#auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=api_key

#input config file for Python API communication with OCI eg /cd3user/tenancies/<prefix>/.config_files/<prefix>_config;
config_file=/cd3user/tenancies/demo/.config_files/demo_oci_config

#Leave the field blank if you want a single outdir or specify outdir_structure_file.properties containing the directory structure for OCI services.
outdir_structure_file=/cd3user/tenancies/demo/demo_outdir_structure_file.properties

#IaC Tool to be configured - Terraform(specify terraform) or OpenTofu(specify tofu)
tf_or_tofu=terraform

#path to cd3 excel eg /cd3user/tenancies/<prefix>/CD3-Customer.xlsx
cd3file=/cd3user/tenancies/demo/CD3-demo.xlsx

#specify create_resources to create new resources in OCI(greenfield workflow)
#specify export_resources to export resources from OCI(non-greenfield workflow)
workflow_type=create_resources
```


<span style="color: teal; font-weight: bold;">Step 3:</span>

Execute the setUpOCI.py script to start creating the terraform/tofu configuration files.
    
Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```
```
python setUpOCI.py /cd3user/tenancies/<prefix>/<prefix>_setUpOCI.properties
```
         
!!! example "Example Execution"

    Updated OCI_Regions file !!!

    Script to fetch the compartment OCIDs into variables file has not been executed.<br>
    Do you want to run it now? (y|n):

⬆️ This prompt appears when executing the toolkit for the very first time or when any new compartments are created using the toolkit. Enter 'y' to fetch the details of compartment OCIDs into variables file.

!!! Note

    Execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after creating Compartments. This step is required every time a compartment is created via the toolkit or via the OCI console.

<br> After fetching the compartment details, the toolkit will display the menu options as shown below:

!!! example  "Example Execution"  
    <img src = "../images/demo_setupocimenu_cli_create.png", width=1500 height=1000> 


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.<br>



<span style="color: teal; font-weight: bold;">Expected Outputs:</span>

The tfvars files for the selected services will be generated at the following path:
`/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>/`


<span style="color: teal; font-weight: bold;">Step 4:</span>

Change the directory to  ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>``` .

  - If **terraform** is selected as the IaC tool initially, execute:


    ```terraform init```  - *To initialize and prepare the working/out directory so Terraform can run the configuration.*<br>

    ```terraform plan```  - *To preview any changes before applying them. Run the plan against <a href="../opa-integration"><u>OPA policies</u></a> for compliance against CIS.*

    ```terraform apply``` - *To make the changes defined by Terraform configuration to create, update, or destroy resources in OCI.*

  
- If **tofu** is selected, execute:

    ```tofu init```  - *To initialize and prepare the working/out directory so tofu can run the configuration.*<br>

    ```tofu plan```  - *To preview any changes before applying them. Run the plan against <a href="../opa-integration"><u>OPA policies</u></a> for compliance against CIS.*

    ```tofu apply``` - *To make the changes defined by tofu configuration to create, update, or destroy resources in OCI.*