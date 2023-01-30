# Automation Toolkit Workflows
CD3 Automation Tool Kit supports 2 main workflows:
1.	Greenfield Tenancies. - Empty OCI tenancy (or) do not need to modify / use any existing resources.
2.	Non-Greenfield Tenancies - Need to use / manage existing resources.  Export existing resources into CD3 & TF State, then use the Greenfield workflow.

## Detailed Steps to execute Automation Toolkit Workflows 
### Green Field Tenancies
Below are the steps that will help to configure the Automation Tool Kit to support the Green Field Tenancies:

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates)

**Step 2**:
<br>Fill the CD3 Excel with appropriate values specific to the client and put at the appropriate location.
<br>Modify/Review [setUpOCI.properties](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#setupociproperties) with **non_gf_tenancy** set to **false** as shown below:

<img src = "https://user-images.githubusercontent.com/103508105/214644389-0539165c-4253-451b-b035-4ae3f5a80a59.png" width=75% height=75%>



**Step 3**:
<br>Execute the SetUpOCI.py script to start creating the terraform configuration files.
    
Command to Execute:
<br>```cd /cd3user/oci_tools/cd3_automation_toolkit/```
<br>**python setUpOCI.py <path_to_setupOCI.properties> ie**
<br>```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
         
→ Example execution of the wrapper script:
   
<img src = "https://user-images.githubusercontent.com/122371432/213680074-be73042e-8672-44f5-b2cf-619998805724.png" width=50% height=50%>

 

Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.


**Step 4:** 
<br>Change your directory to _/cd3user/tenancies/<customer\_name>/terraform\_files/<region\_dir>/_  and Execute:

**terraform init**  - To initialize and prepare your working/out directory soTerraform can run the configuration.<br>
**terraform plan**  - To preview any changes before you apply them.<br>
**terraform apply** - To make the changes defined by Terraform configuration to create, update, or destroy resources in OCI.
  
> **Note**  

>Execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after you create Compartments. This is a required step everytime you create a compartment via toolkit or via the OCI console.
  
  
 </br> 
  
 ### Non-Green Field Tenancies

  > **Note**
   
  >Course of actions involved in Exporting objects from OCI-     
  > * Automation Tool Kit fetches the data for the cd3 supported services from all the regions the tenancy is subscribed to. Data is written to appropriate sheets of the CD3 based on the resources being exported.
  > * Tool Kit then generates the TF configuration files/auto.tfvars files for these exported resources.
  > * It also generates a shell script - tf_import_commands_`<resource>`_nonGF.sh that has the import commands, to import the state of the resources to tfstate file.(This helps to manage the resources via Terraform in future). 

  
Below are the steps that will help to configure the Automation Tool Kit to support the Non - Green Field Tenancies:

**Step 1:** 
<br>Chose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates)
 
**Step 2:** 
<br>Put CD3 Excel at the appropriate location.
<br>Modify/Review [setUpOCI.properties](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#setupociproperties) with **non_gf_tenancy** set to **true**  as shown below:
<img src = "https://user-images.githubusercontent.com/103508105/214645849-464ea32f-31b9-4c4a-8d0c-31e4e3cb541b.png" width=75% height=75%>

  
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
>   Once the export (including the execution of **tf_import_commands_`<resource>`_nonGF.sh**) is complete, switch the value of **non_gf_tenancy** back to **false**. 
>   This allows the Tool Kit to support the tenancy as Green Field from this point onwards.

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Essentials_of_Automation_Toolkit.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/RestructuringOutDirectory.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>


