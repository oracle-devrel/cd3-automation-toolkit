# Export and Manage Resources from OCI (Non-Greenfield Workflow)

!!! important
    - Toolkit will **over-write** the data in specific tabs of CD3 Excel sheet with exported content from OCI while the other tabs remain intact.
    - Differential state import of the objects will be performed, ie the import statements will be generated only for the objects which are not already there in state file.
    - While exporting same service multiple times, be cautious to review the terraform plan changes and then apply.

**Step 1:** 
<br>Choose the Blank CD3 Excel sheet template from <a href="../excel-templates"><u>Excel Templates</u></a>
 and copy at _/cd3user/tenancies/<prefix\>/_<br><br>
**Step 2:** 
<br>Modify ```/cd3user/tenancies/<prefix>/<prefix>_setUpOCI.properties``` 
<br>Add the location of CD3 excel file under **cd3file** parameter and set **workflow_type** to **export_resources**  as shown below.
<br> The other parameters are already updated with correct values.
```ini
#Input variables required to run setUpOCI script

#path to output directory where terraform files will be generated. eg /cd3user/tenancies/<prefix>/terraform_files
outdir=/cd3user/tenancies/demotenancy/terraform_files/

#prefix for output terraform files eg <customer_name> like demo
prefix=demo

#auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=api_key

#input config file for Python API communication with OCI eg /cd3user/tenancies/<prefix>/.config_files/<prefix>_config;
config_file=/cd3user/tenancies/demotenancy/.config_files/demotenancy_oci_config

#Leave it blank if you want single outdir or specify outdir_structure_file.properties containing directory structure for OCI services.
outdir_structure_file=/cd3user/tenancies/demotenancy/demotenancy_outdir_structure_file.properties

#IaC Tool to be configured - Terraform(specify terraform) or OpenTofu(specify tofu)
tf_or_tofu=terraform

#path to cd3 excel eg /cd3user/tenancies/<prefix>/CD3-Customer.xlsx
cd3file=/cd3user/tenancies/demo/CD3-demo.xlsx

#specify create_resources to create new resources in OCI(greenfield workflow)
#specify export_resources to export resources from OCI(non-greenfield workflow)
workflow_type=export_resources
```
  
**Step 3:** 
<br>Execute the setUpOCI.py script to start exporting the resources to CD3 and creating the terraform/tofu configuration files.

Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```

```
python setUpOCI.py /cd3user/tenancies/<prefix>/<prefix>_setUpOCI.properties
```

!!! example  "Example Execution"

    Updated OCI_Regions file !!!

    Script to fetch the compartment OCIDs into variables file has not been executed.<br>
    Do you want to run it now? (y|n):

⬆️ The above prompt appears when executing the toolkit for the very first time or when any new compartments are created using the toolkit. Enter 'y' to fetch the details of compartment OCIDs into variables file.

!!! Note

    Execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after creating Compartments. This step is required every time a compartment is created via the toolkit or via the OCI console.

<br>⬇️ After fetching the compartment details, users have options to export their resources only from specific regions, compartments, and resources with specific Tags if required. The toolkit will display the menu options as shown below:


!!! example  "Example Execution"

      <img src = "../images/demo_setupocimenu_cli_export.png" width=100% height=100%>


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.
  

**Expected Outputs:**

a. Excel sheet with the resource details from OCI.<br> 
b. Configuration files - <b><i>*.auto.tfvars</i></b> <br> 
c. Shell Script with import commands - <b><i>import_commands_`<resource>`.sh</i></b>


**Step 4:** 

Execute the <b>*import_commands_`<resource>`.sh*</b> files that are generated in the outdir.
<br>The terraform/tofu plan should show that infrastructure is up-to-date with no changes required for all regions.
  

!!! note
    - Once the export (including the execution of **import_commands_`<resource>`.sh**) is complete, switch the value of **workflow_type** back to **create_resources**. This allows the toolkit to modify these resources or create new ones on top of them.
