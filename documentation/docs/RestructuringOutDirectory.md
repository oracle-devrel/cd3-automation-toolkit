# Grouping of generated Terraform files (Creating independent tfstate files for each resource)
The CD3 Automation Toolkit was previously built to generate all the output Terraform files within a designated region directory.
OCI components like - Network, Instances, LBaaS, Databases etc., were maintained in a single tfstate file.
This was not a viable option for tenancies requiring huge infrastructure.

Starting with the Automation Toolkit release v10.1, it is now possible to select separate directories for each Oracle Cloud Infrastructure (OCI) service supported by the toolkit.

This can be configured while [connecting your container to the OCI tenancy](Connect_container_to_OCI_Tenancy.md).

A new parameter 'outdir_structure_file' has been introduced in tenancyconfig.properties using which can be used to configure single outdir or different outdir for each service.

To enable independent service directories for the generated Terraform files, follow the below steps:

1. Go to ``` /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/tenancyconfig.properties```. Enter required config details. 

   Users have the option to enable or disable multiple service outdirectories based on their specific requirements.

   To enable it, uncomment the *outdir_structure_file* parameter which has the pre-defined path to *outdir_structure_file.properties*. Refer to the screenshot below:
   ![image](https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/0c4ecb2f-6e35-4c93-9976-4aed2e74aca6)

<br>
2. Under the same user-scripts folder, open *outdir_structure_file.properties* and modify the directory names if required. They are in the                                                    format:*OCI_Service_Name=Directory_Name*.
   > Note: 
   > * Do not modify the OCI service Names specified on the left hand side.Modify the directory name specified on Right Hand Side
   > * Directory will be created for that service under <region> directory. Do not provide absolute path.
   > * To make any changes to the directory structure later, it is necessary to rerun the "createTenancy.py" script from scratch.
   > * It is mandatory to specify the directory name for each service.
  
   <img width="953" alt="image" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/cf6eb85d-30ad-4de4-8164-963a36076128">

   Here, the network and nsg directories have been renamed to **demo_network** and **demo_nsg** respectively. The next steps to run the toolkit remain the same as specified in                  [Greenfield workflow](GreenField.md)

  
 3. Run ```python createTenancyConfig.py tenancyconfig.properties ``` from user-scripts folder.
  
 4.	Go to ```/cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.propertiesfile ``` and add the CD3 Excel path. 
      
     Change to the below directory
     <br>```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   
     Run the script<br>```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
     
     Select required options. *(Here,"Network", "nsg" options have been selected to verify the files under the "demo_network", "demo_nsg" folders)*
   
     *auto.tfvars* for the respective services are created.
  
  5. Go to the region directory ```/cd3user/tenancies/<customer_name>/terraform_files/<region>/``` . It is clear that all the service-specific folders have been created              successfully.
  
     <img width="953" alt="image" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/ff018b02-225b-4fc1-89c1-c671978b3fa4">
   
  
  6. Navigate to the **demo-network** folder. All the auto.tfvars and tfstate files related to Network service can be seen within the **demo_network** folder. Terraform operations like        terraform init, terraform plan, terraform apply etc., will be executed from within these folders.
  
      <img width="953" alt="image" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/c2eaa16b-03ab-4c91-acfa-8a23843b6bc3">
   
     
     Similarly for all the services, their respective auto.tfvars and tfstate files get grouped under their assigned directories. This makes it much easier to manage OCI resources using          terraform for large-scale infrastructures.
   
     Likewise, While doing an export from OCI to terraform, update the *tenancyconfig.properties* file with path to *outdir_structure_file.properties* similar to step1 and then follow the      steps to run the toolkit for [Non-green field tenancies](NonGreenField.md). With this, all the .sh files with import                      commands of a particular OCI service are grouped and can be easily managed.
  
    
  
 



   
