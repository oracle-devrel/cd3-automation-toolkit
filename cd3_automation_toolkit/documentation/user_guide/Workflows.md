## Automation Toolkit Workflows
CD3 Automation Tool Kit supports 2 main workflows:
1.	Greenfield Tenancies. - Empty OCI tenancy (or) do not need to modify / use any existing resources.
2.	Non-Greenfield Tenancies - Need to use / manage existing resources.  Export existing resources into CD3 & TF State, then use the Greenfield workflow.

## Steps to execute Automation Toolkit Workflows 
### Green Field Tenancies
Below are the steps that will help to configure the Automation Tool Kit to support the Green Field Tenancies:

**Step 1**: 

The CD3 Template can be found at location  - /cd3user/oci_tools/cd3_automation_toolkit/example.

For the Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases) - use the **CD3-SingleVCN-template.xlsx** file or **CD3-HubSpoke-template.xlsx** or **CD3-CIS-template.xlsx** based on the requirement.
 
For Events, Notifications, Alarms and Service Connector Hub - use the **CD3-CIS-ManagementServices-template.xlsx** file.



**Step 2**:

Fill the CD3 file with appropriate values specific to the client and put at the appropriate location.
              
Modify/Review **setUpOCI.properties**: (**non_gf_tenancy** set to **false**)

<img src = "https://user-images.githubusercontent.com/122371432/213668401-9e795546-6683-42ab-8ce0-9c9c72b84079.png" width=75% height=75%>



**Step 3**:

Execute the SetUpOCI.py script to start creating the terraform configuration files.
        
Command to Execute:
**python setUpOCI.py <path_to_setupOCI.properties>**
         
Example execution of the wrapper script:
   
<img src = "https://user-images.githubusercontent.com/122371432/213680074-be73042e-8672-44f5-b2cf-619998805724.png" width=50% height=50%>

 

Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.


**Step 4:** 

Change your directory to /cd3user/tenancies/<customer_name>/terraform_files/region_dir/  and Execute:

**terraform init**  - To initialize and prepare your working/out directory soTerraform can run the configuration.<br>
**terraform plan**  - To preview any changes before you apply them.<br>
**terraform apply** - To make the changes defined by Terraform configuration to create, update, or destroy resources in OCI.
  
> **Note**  

>Make sure to execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu after you create Compartments. This will ensure that the variables file in outdir is updated with the OCID information of all the compartments.
  
  
 </br> 
  
 ### Non-Green Field Tenancies

  > **Note**
   
  >Course of actions involved in Exporting objects from OCI-     
  > * Automation Tool Kit fetches the data for the cd3 supported services from all the regions the tenancy is subscribed to. Data is written to appropriate sheets of the CD3 based on the resources being exported.
  > * Tool Kit then generates the TF configuration files/auto.tfvars files for these exported resources.
  > * It also generates a shell script - tf_import_commands_<resource>_nonGF.sh that has the import commands, to import the state of the resources to tfstate file.(This helps to manage the resources via Terraform in future). 

  
Below are the steps that will help to configure the Automation Tool Kit to support the Non - Green Field Tenancies:

**Step 1:** 
 
Choose the right CD3 format for exporting the contents from OCI.
  
   
Two different formats of CD3 to be used : (An example of these files can be found at location - /cd3user/oci_tools/cd3_automation        _toolkit/example or can be downloaded from cd3)

**CD3-Blank-template.xlsx** - Use this format of the Excel sheet to export objects like Network Components, Identity Components,         Core Infra Components , DB Components and Tags. 

**CD3-CIS-ManagementServices-template.xlsx** - Use this format of the Excel sheet to export Events, Notifications, Alarms and           Service Connector Hub.

 
**Step 2:** 
 
Fill up/review the **setUpOCI.properties** file.
  
Once the CD3 format is chosen, fill the sheets with appropriate values and put it at the appropriate location.
         
Modify **setUpOCI.properties** as shown below: (**non_gf_tenancy** set to **true**)

<img src = "https://user-images.githubusercontent.com/122371432/213680179-ae2e78b8-f508-47b1-8fb5-23d635d78648.png" width=75% height=75%>

  
**Step 3:** 
 
Execute the SetUpOCI.py script to start exporting the resources to CD3 and creating the terraform configuration files.

Command to Execute:
**python setUpOCI.py <path_to_setupOCI.properties>**
  
Example execution of the wrapper script:
  
<img src = "https://user-images.githubusercontent.com/122371432/213680233-002cce49-65c3-4cab-8f38-ef56f04fe266.png" width=50% height=50%>


Choose the resources by specifying a single option (for choosing one of these resources) or comma-separated values (to choose multiple resources) as shown in the sample screenshot above.
  
Make sure to execute **"Fetch Compartments OCIDs to variables file"** from **CD3 Services** in setUpOCI menu at least once. This will       ensure that the variables file in outdir is updated with the OCID information of all the compartments.
  
Tabs- Exported OCI data will over-write to the specific CD3 sheets while the other sheets remain intact.
 
 </br>

**Expected Outputs:**
  
a. Excel sheet with the resource details from OCI
  
b. Terraform Configuration files - *.auto.tfvars
  
c. Shell Script with import commands - tf_import_commands_<resource>_nonGF.sh 
      
**Action:** Execute the tf_import_commands_<resource>_nonGF.sh files that are generated in the outdir.
  
The terraform plan should show that infrastructure is up-to-date with no changes required for all regions.
  
<img src = "https://user-images.githubusercontent.com/122371432/213680328-ff972472-5c96-424e-b616-9f4c217eb4ca.png" width =50% height=50%>



