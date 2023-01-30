## Frequently Asked Questions
 
**Q 1. Is there a way to verify my input CD3 Excel sheet for any typos/miskates?**
<br> **Ans**  Yes, please choose 'Validate CD3' option in setUpOCI menu in GreenField workflow. You can choose to validate specific tabs of the Excel sheet. Please see
[CD3 Validator Features](/cd3_automation_toolkit/documentation/user_guide/learn_more/SupportForCD3Validator.md#support-for-cd3-validator) for more details.

**Q 2. Can I use an existing outdir to export the data from OCI?**
<br> **Ans** Make sure to use a clean outdir without any .tfvars or .tfstate file. Also use a blank CD3 Excel sheet as export process will overwrite the data in the respective tab.

**Q 3. If I am already using the toolkit and my OCI tenancy has been subscribed to a new region, how do i use the new region with toolkit?**
<br> **Ans** Follow below steps to start using the newly subscribed region with the toolkit:
<br>           - Take backup of the existing out directory.
<br>           - Create a new directory for the region say 'london' along with outher region directories.
<br>           - Copy all the terraform modules and .tf files, except the .auto.tfvars and .tfstate files from existing region directory to the new one
<br>           - Modify the name of variables file (eg variables_london.tf)
<br>           - Modify the region parameter in tis variables_london.tf


**Q 4. How do I upgrade an existing version of the toolkit to the new one without disrupting my existing tenancy files/directories?**
<br> **Ans** 

**Q 5. I am getting 'Permission Denied' error while executing any commands inside the container.**
<br> **Ans** When you are running the docker container from a Linux OS, if the outdir is on the root, you may get a permission denied error while executing steps like createAPIKey.py. In such scenarios, please follow the steps given below -
<br><br>**Error Screenshot:**
![image](https://user-images.githubusercontent.com/103508105/215454472-2367c5d5-2dce-4248-a7fd-c57f1104267e.png)
<br><br>**Solution:**
<br>Please change:
<br>           - selinux mode from Enforcing to Permissive
<br>           - change the owner of folders in /cd3user/tenancies to that of cd3user. 
Please refer the screenshots below -
![image](https://user-images.githubusercontent.com/103508105/215455637-4bcaac18-269d-4029-b273-2214b719563f.png)
<br>           - Alternately, please attach a data disk and map the container (/cd3user/tenancies) on a folder that is created on the data disk (your local folder).




