# Frequently Asked Questions
 
**1. Is there a way to verify my input CD3 Excel sheet for any typos/miskates?**
<br>   
 	   Yes, please choose 'Validate CD3' option in setUpOCI menu in GreenField workflow. It validates specific tabs of the excel sheet. Please see
 	   [CD3 Validator Features](/cd3_automation_toolkit/documentation/user_guide/learn_more/SupportForCD3Validator.md#support-for-cd3-validator) for more          details.

**2. Can I use an existing outdir to export the data from OCI?**
<br> 

   Make sure to use a clean outdir without any .tfvars or .tfstate file. Also use a blank CD3 Excel sheet as export process will overwrite the data in the    respective tab.

**3. If I am already using the toolkit and my OCI tenancy has been subscribed to a new region, how do i use the new region with toolkit?**
<br>  
Follow below steps to start using the newly subscribed region with the toolkit:
<br>           - Take backup of the existing out directory.
<br>           - Create a new directory for the region say 'london' along with other region directories.
<br>           - Copy all the terraform modules and .tf files, except the .auto.tfvars and .tfstate files from existing region directory to the new one
<br>           - Modify the name of variables file (eg variables_london.tf)
<br>           - Modify the region parameter in this variables_london.tf
<br>           - Modify Image OCIDs in this variables file according to new region.


**4. How do I upgrade an existing version of the toolkit to the new one without disrupting my existing tenancy files/directories?**
<br>  
Please look at the latest release information under <a href = https://github.com/oracle-devrel/cd3-automation-toolkit/releases>Releases. </a>

**5. How do I export instances in batches using different filters?**
<br>  
Follow below steps:
<br>          - Modify the setUpOCI.properties file to set non_gf_tenancy to "true".
<br>          - Choose "Export Compute".
<br>          - Specify the filter - prefix of the instances or specific AD to export.
<br>          - Once the execution completes, take a backup of the files generated for instances in out directory( _<customer\_name>\__instances.tfvars_ and _tf\_import\_cmds \_instances\_nonGF.sh_) and a backup of the 'Instances' tab of the Input CD3 Excel Sheet.
<br>          - Repeat steps from 1 to 4 to export next set of Instances using another filter.
<br>          - Once you export all the required instances using multiple filters, move the files from backup to the out directory and then execute all the shell scripts generated for Instances. Consolidate the data of exported instances from the Excel sheet backups.



**6. How do I delete a compartment from OCI using the toolkit?**
<br>

Terraform destroy on compartments or removing the compartments details from _<customer\_name>\_compartments.auto.tfvars_ will not delete them from OCI Console by default. Inorder to destroy them from OCI either - 
<br>           - Add an additional column - _enable\_delete_ to Compartments Tab of CD3 Excel sheet with the value _TRUE_ for the compartments that needs to be deleted on terraform destroy. Execute the toolkit menu option to Create Compartments.</li>
  <br>(OR)
<br>           - Add _enable\_delete = true_ parameter to each of the compartment that needs to be deleted in _<customer\_name>\_compartments.auto.tfvars_
 

**7. I am getting 'Permission Denied' error while executing any commands inside the container.**
<br> 

When you are running the docker container from a Linux OS, if the outdir is on the root, you may get a permission denied error while executing steps like createAPIKey.py. In such scenarios, please follow the steps given below -
<br><br>**Error Screenshot:**
![image](https://user-images.githubusercontent.com/103508105/215454472-2367c5d5-2dce-4248-a7fd-c57f1104267e.png)
<br><br>**Solution:**
<br>Please change:
<br>           - selinux mode from Enforcing to Permissive
<br>           - change the owner of folders in /cd3user/tenancies to that of cd3user. 
Please refer the screenshots below -
![image](https://user-images.githubusercontent.com/103508105/215455637-4bcaac18-269d-4029-b273-2214b719563f.png)
<br>           - Alternately, please attach a data disk and map the container (/cd3user/tenancies) on a folder that is created on the data disk (your local folder).

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/KnownBehaviour.md">:arrow_backward: Prev</a> | <a href="/README.md#table-of-contents-bookmark">Next :arrow_forward:</a> |
| :---- | -------: |
