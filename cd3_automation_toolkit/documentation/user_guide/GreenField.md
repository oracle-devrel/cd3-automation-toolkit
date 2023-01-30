# Green Field Tenancies

## Detailed Steps
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
