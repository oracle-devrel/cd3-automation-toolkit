# **Create and Manage Resources in OCI (Greenfield Workflow)**
---

**Step 1**: 
<br>Choose the appropriate excel sheet template from [Excel Templates](excel-templates.md).
Fill the excel with appropriate values and copy at _/cd3user/tenancies/<customer_name\>_<br><br>
**Step 2**:
<br>Modify ```/cd3user/tenancies /<customer_name>/<customer_name>_setUpOCI.properties```.
<br>Update parameters: **cd3file** parameter to the location of CD3 excel file and  **workflow_type**  to **create_resources** as shown below.
<br> The other parameters are already updated with correct values.
```ini
#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_name>/terraform_files
outdir=/cd3user/tenancies/demo/terraform_files/

#prefix for output terraform files eg <customer_name> like demo
prefix=demo

# auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=api_key

#input config file for Python API communication with OCI eg /cd3user/tenancies/<customer_name>/.config_files/<customer_name>_config;
config_file=/cd3user/tenancies/demo/.config_files/demo_oci_config

# Leave it blank if you want single outdir or specify outdir_structure_file.properties containing directory structure for OCI services.
outdir_structure_file=/cd3user/tenancies/demo/demo_outdir_structure_file.properties

#path to cd3 excel eg /cd3user/tenancies/<customer_name>/CD3-Customer.xlsx
cd3file=/cd3user/tenancies/demo/CD3-demo.xlsx

#specify create_resources to create new resources in OCI(greenfield workflow)
#specify export_resources to export resources from OCI(non-greenfield workflow)
workflow_type=create_resources
```

**Step 3**:
<br>Execute the setUpOCI.py script to start creating the terraform configuration files.
    
Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```
```
python setUpOCI.py  <path_to_setupOCI.properties>
``` 
i.e. 
```
python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
```
         
!!! example  "example execution of the wrapper script"

    Updated OCI_Regions file !!!

    Script to fetch the compartment OCIDs into variables file has not been executed.<br>
    Do you want to run it now? (y|n):

→ This prompt appears when you run the toolkit for the very first time or when any new compartments are created using the toolkit. Enter 'y' to fetch the details of compartment OCIDs into variables file.
<br>→ After fetching the compartment details, the toolkit will display the menu options as shown below:

!!! example  "example execution of the wrapper script"   
    <img src = "/images/cliGF-1.png" width=90% height=90%>


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.

**Expected Outputs:**
<br>It will generate tfvars files for the services selected at _/cd3user/tenancies/<customer_name\>/terraform_files/<region_dir\>/<service_dir\>/_

**Step 4:** 
<br>Change your directory to  ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/<service_dir>```  and Execute:

**terraform init**  - To initialize and prepare your working/out directory so Terraform can run the configuration.<br>

**terraform plan**  - To preview any changes before you apply them. Run the plan against [OPA policies](/opa-integration.md) for compliance against CIS.

**terraform apply** - To make the changes defined by Terraform configuration to create, update, or destroy resources in OCI.
  
!!! Note

    Execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after you create Compartments. This is a required step everytime you create a compartment via toolkit or via the OCI console.