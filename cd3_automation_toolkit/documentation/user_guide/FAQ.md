## Frequently Asked Questions
 
**Q 1. Is there a way to verify the input CD3 Excel sheet for any typos/miskates?**
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

**Q 4. How do I upgrade to the new version of toolkit for my existing OCI tenancies?**
