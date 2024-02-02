# Export Resources from OCI (Non-Greenfield Workflow)

  > **Note**
   
  >Course of actions involved in Exporting objects from OCI-     
  > * Automation Tool Kit fetches the data for the supported services. You can chose to export the data from a specific region or the compartment. Exported data is written to appropriate sheets of the CD3 Excel Sheet based on the resources being exported.
  > * Tool Kit then generates the TF configuration files/auto.tfvars files for these exported resources.
  > * It also generates a shell script - tf_import_commands_`<resource>`_nonGF.sh that has the import commands, to import the state of the resources to tfstate file.(This helps to manage the resources via Terraform in future). 


**Step 1:** 
<br>Chose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates)
 
**Step 2:** 
<br>Put CD3 Excel at the appropriate location.
<br>Modify/Review [setUpOCI.properties](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#setupociproperties) with **workflow_type** set to **export_resources**  as shown below:
```ini
#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_name>/terraform_files
outdir=/cd3user/tenancies/demotenancy/terraform_files/

#prefix for output terraform files eg <customer_name> like demotenancy
prefix=demotenancy

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
<br>Execute the SetUpOCI.py script to start exporting the resources to CD3 and creating the terraform configuration files.

Command to Execute:
<br>```cd /cd3user/oci_tools/cd3_automation_toolkit/```
<br>**python setUpOCI.py <path_to_setupOCI.properties> ie**
<br>```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
  
→ Example execution of the wrapper script:
  
<img src = "https://user-images.githubusercontent.com/122371432/213680233-002cce49-65c3-4cab-8f38-ef56f04fe266.png" width=50% height=50%>


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.
  
Make sure to execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu at least once. This will       ensure that the variables file in outdir is updated with the OCID information of all the compartments.
  
> Toolkit will over-write the specific tabs of CD3 Excel sheet with exported data for that resource in OCI while the other tabs remain intact.
 
 </br>

**Expected Outputs:**
<br>a. Excel sheet with the resource details from OCI  
b. Terraform Configuration files - *.auto.tfvars  
c. Shell Script with import commands - tf_import_commands_`<resource>`_nonGF.sh 
      
**Action:**
<br>Execute the tf_import_commands_`<resource>`_nonGF.sh files that are generated in the outdir.
<br>The terraform plan should show that infrastructure is up-to-date with no changes required for all regions.
  
<img src = "https://user-images.githubusercontent.com/122371432/213680328-ff972472-5c96-424e-b616-9f4c217eb4ca.png" width =50% height=50%>

> **Note**<br>
>   Once the export (including the execution of **tf_import_commands_`<resource>`_nonGF.sh**) is complete, switch the value of **workflow_type** back to **create_resources**. 
>   This allows the Tool Kit to support the tenancy as Green Field from this point onwards.

## Example - Export Identity
Follow the below steps to quickly export Identity components from OCI.

1. Use the excel [CD3-Blank-template](/cd3_automation_toolkit/example) and place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.

2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _workflow_type_ parameter value to _export_resources_. (for Non Greenfield Workflow.)
     
3. Change Directory to 'cd3_automation_toolkit' :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
 4. Choose option 'Export Identity' from the displayed menu. Once the execution is successful, you will see:
      <ul>
      <li><b>Filled in tabs</b>-<i>Compartments, Groups, Polecies of Excel sheet</i></li>
      <li><i>tf_import_commands_identity_nonGF.sh</i></li>
      <li><i>&lt;customer_name>_compartments.auto.tfvars, &lt;customer_name>_groups.auto.tfvars, &lt;customer_name>_policies.auto.tfvars</i></li>
      </ul>
   
 5. Execute _tf\_import\_commands\_identity_nonGF.sh_ to start importing the identity components into tfstate file.
 6. Repeat the above process (except Step 5) to export other components from OCI.
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosGF.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosNGF.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>

