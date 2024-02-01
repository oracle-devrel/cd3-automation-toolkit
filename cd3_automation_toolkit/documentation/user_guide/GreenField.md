# Create resources in OCI (Greenfield Workflow)

## Detailed Steps
Configure the Automation Toolkit to create new resources in tenancies:

**Step 1**: 
<br>Choose the appropriate Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates)

**Step 2**:
<br>Fill the Excel with appropriate values and put at the appropriate location.
<br>Modify/Review [setUpOCI.properties](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#setupociproperties) with **workflow_type** set to **create_resources** as shown below:
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
workflow_type=create_resources
```

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

**terraform plan**  - To preview any changes before you apply them. Run the plan against [OPA policies](/cd3_automation_toolkit/documentation/user_guide/learn_more/OPAForCompliance.md) for compliance against CIS.

**terraform apply** - To make the changes defined by Terraform configuration to create, update, or destroy resources in OCI.
  
> **Note**  

>Execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after you create Compartments. This is a required step everytime you create a compartment via toolkit or via the OCI console.
   
 </br>
 
 ## Example - Create a Compartment

Follow the below steps to quickly provision a compartment on OCI.

1. Use the excel [CD3-SingleVCN-template](/cd3_automation_toolkit/example) and fill the required Compartment details in the 'Compartments' tab.

   Make appropriate changes to the template. For Eg: Update the _Region_ value to your tenancy's home region.
   
   Once all the required data is filled in the Excel sheet, place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your    local directory.
   
2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _workflow_type_ parameter value to _false_. (for Greenfield Workflow.)
  
3. Change Directory to 'cd3_automation_toolkit' :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose option to create compartments under 'Identity' from the displayed menu. Once the execution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
5. Choose _Fetch Compartments OCIDs to variables file_ under _CD3 Services_ in setUpOCI menu. Execute the command to fetch the details of the                 compartments if it already exists/ created in OCI. These details will be written to the terraform variables file.

6. Repeat the above process (except Step 5) to create other components in OCI.
 
 <br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/learn_more/OPAForCompliance.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
