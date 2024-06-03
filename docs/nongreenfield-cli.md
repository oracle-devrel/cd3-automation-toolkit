# Export and Manage Resources from OCI (Non-Greenfield Workflow)

!!! note
    - Make sure that service for which export is done does not have existing tfvars/state file.<br>


**Step 1:** 
<br>Chose the Blank CD3 Excel sheet template from [Excel Templates](excel-templates.md)
 and copy at _/cd3user/tenancies/<customer_name\>_<br><br>
**Step 2:** 
<br>Modify ```/cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties``` 
<br>Update parameters: **cd3file** parameter to the location of CD3 excel file and **workflow_type** to **export_resources**  as shown below.
<br> The other parameters are already updated with correct values.
```ini
#Input variables required to run setUpOCI script

#path to output directory where terraform files will be generated. eg /cd3user/tenancies/<customer_name>/terraform_files
outdir=/cd3user/tenancies/demotenancy/terraform_files/

#prefix for output terraform files eg <customer_name> like demo
prefix=demo

# auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=api_key

#input config file for Python API communication with OCI eg /cd3user/tenancies/<customer_name>/.config_files/<customer_name>_config;
config_file=/cd3user/tenancies/demotenancy/.config_files/demotenancy_oci_config

# Leave it blank if you want single outdir or specify outdir_structure_file.properties containing directory structure for OCI services.
outdir_structure_file=/cd3user/tenancies/demotenancy/demotenancy_outdir_structure_file.properties

#path to cd3 excel eg /cd3user/tenancies/<customer_name>/CD3-Customer.xlsx
cd3file=/cd3user/tenancies/demotenancy/CD3-Blank-template.xlsx

#specify create_resources to create new resources in OCI(greenfield workflow)
#specify export_resources to export resources from OCI(non-greenfield workflow)
workflow_type=export_resources
```
  
**Step 3:** 
<br>Execute the setUpOCI.py script to start exporting the resources to CD3 and creating the terraform configuration files.

Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```

```
python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
```

!!! example  "Example Execution"

    Updated OCI_Regions file !!!

    Script to fetch the compartment OCIDs into variables file has not been executed.<br>
    Do you want to run it now? (y|n):

→ This prompt appears when executing the toolkit for the very first time or when any new compartments are created using the toolkit. Enter 'y' to fetch the details of compartment OCIDs into variables file.

!!! Note

    Execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after creating Compartments. TThis step is required every time a compartment is created via the toolkit or via the OCI console.

<br>→ After fetching the compartment details, the toolkit will display the menu options as shown below:


!!! example  "Example Execution"

      <img src = "../images/demo_setupocimenu_cli_export.png" width=90% height=90%>


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.
  

**Expected Outputs:**

<br>a. Excel sheet with the resource details from OCI.<br> 
b. Terraform Configuration files - *.auto.tfvars  
c. Shell Script with import commands - tf_import_commands_`<resource>`_nonGF.sh 

!!! info 
    Toolkit will over-write the specific tabs of CD3 Excel sheet with exported data for that resource in OCI while the other tabs remain intact.

**Step 4:** 

<br>Execute the tf_import_commands_`<resource>`_nonGF.sh files that are generated in the outdir.
<br>The terraform plan should show that infrastructure is up-to-date with no changes required for all regions.
  

!!! note
    - Once the export (including the execution of **tf_import_commands_`<resource>`_nonGF.sh**) is complete, switch the value of **workflow_type** back to **create_resources**. This allows the toolkit to modify these resources or create new ones on top of them.
