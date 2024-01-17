# Export Resources from OCI via Jenkins(Non-Greenfield Workflow)

  > **Note**
   
  >Course of actions involved in Exporting objects from OCI-     
  > * Automation ToolKit fetches the data for the supported services. You can chose to export the data from a specific region or the compartment. Exported data is written to appropriate sheets of the input Excel Sheet based on the resources being exported.
  > * Toolkit then generates the TF configuration files/auto.tfvars files for these exported resources.
  > * It also generates a shell script - tf_import_commands_`<resource>`_nonGF.sh that has the import commands, to import the state of the resources to tfstate file.(This helps to manage the resources via Terraform in future). 

## Detailed Steps
Below are the steps that will help to execute setUpOCI pipeline to export existing resources from tenancies:

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates)
Chose CD3-Blank-template.xlsx for an empty sheet.

**Step 2**:
<br>Login to Jenkins URL with user created after initialization and click on setUpOCI pipeline from Dashboard. Click on 'Build with Parameters' from left side menu.
<img width="872" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/7c71d75d-b3cd-478c-8275-b6385e3b427b">


**Step 3**:
<br>Upload the above chosen excel sheet in Excel_Template section.


<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/25d720c5-fa23-49a4-b80e-663eae179753">

**Step 4:** 
<br>Select the workflow as 'Export Resources from OCI(Non-Greenfield Workflow). Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows export of Network and Compute.

<img width="554" alt="Screenshot 2024-01-17 at 7 11 42 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/9fe46cac-85ad-41df-b5dc-98e2bff9a3a0">

**Step 5:** 
<br>Specify region and compartment from where you want to export the data.
<br>It also asks for service specific filters like display name patterns for compute. Leave empty if no filter needs to be specified.

<img width="835" alt="Screenshot 2024-01-17 at 7 10 56 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/15caac4e-847e-4ea5-9ab5-df8c4ecc56af">
<br>Click on Build at the bottom.<br><br>


**Step 6:**
<br>setUpOCI pipline is triggered and stages are executed as shown below: 

<img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/e0e96b67-e088-47b7-b241-50afdde0d327">

Execute setUpOCI pipeline with workflow selected as 'Export Resources from OCI(Non-Greenfield Workflow). Choose single or multiple options as required. Below screenshot shows export of Identity and Tags.
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

## Example - Export Identity
Follow the below steps to quickly export Identity components from OCI.

1. Use the excel [CD3-Blank-template](/cd3_automation_toolkit/example) and place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.

2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _true_. (for Non Greenfield Workflow.)
     
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

| <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField-Jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>