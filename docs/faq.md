# Frequently Asked Questions
 
**1. Is there a way to verify my input CD3 Excel sheet for any typos/miskates?**
<br>   
 	   Yes, choose 'Validate CD3' option in setUpOCI menu in create_resources (GreenField) workflow. It validates specific tabs of the excel sheet. Check out [CD3 Validator Features](cd3validator.md) for more details.

**2. Can I use an existing outdir to export the data from OCI?**
<br> 

   Make sure to use a clean outdir without any .tfvars or .tfstate file. Also use a blank CD3 Excel sheet as export process will overwrite the data in the    respective tab.

**3. If I am already using the toolkit and my OCI tenancy has been subscribed to a new region, how do i use the new region with toolkit?**
<br>  
Re-run createTenancyConfig.py with same details in tenancyConfig.properties file. It will keep existing region directories as is and create new directory for newly subscribed region.

**4. How do I upgrade an existing version of the toolkit to the new one without disrupting my existing tenancy files/directories?**
<br>  
 Check out [Steps to Upgrade Your Toolkit.](upgrade-toolkit.md)

**5. How do I export instances in batches using different filters?**
<br>  
Follow below steps:

  - Modify the setUpOCI.properties file to set non_gf_tenancy to "true".
  - Choose "Export Compute".
  - Specify the filter - prefix of the instances or specific AD to export.
  - Once the execution completes, take a backup of the files generated for instances in out directory( *<prefix\>\_instances.     tfvars* and _import\_cmds \_instances\_nonGF.sh_) and a backup of the 'Instances' tab of the Input CD3 Excel Sheet.
  - Repeat steps from 1 to 4 to export next set of Instances using another filter.
  - After exporting all the required instances using multiple filters, move the files from backup to the out directory, and then execute all the shell scripts generated for instances. Consolidate the data of exported instances from the Excel sheet backups.


**6. How do I delete a compartment from OCI using the toolkit?**
<br>

Terraform destroy on compartments or removing the compartments details from *<prefix\>\_compartments.auto.tfvars* will not delete them from OCI Console by default. Inorder to destroy them from OCI . 
Either - 
<br>           - Add an additional column - _enable\_delete_ to Compartments Tab of CD3 Excel sheet with the value _TRUE_ for the compartments that needs to be deleted on terraform destroy. Execute the toolkit menu option to Create Compartments.</li>
  <br>(OR)
<br>           - Add _enable\_delete = true_ parameter to each of the compartment that needs to be deleted in _<prefix\>\_compartments.auto.tfvars_
 

