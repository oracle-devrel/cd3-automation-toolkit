## Recommendations

1. Use the **Validate** option in **SetUpOCI** menu to validate the syntax/typos in your input CD3 Excel sheet.
2. For the Non-Greenfield Tenancies, please use a clean out directory (Make sure to not have any **.auto.tfvars** or **terraform.tfstate** in the outdir) and a blank CD3 file -
**CD3-Blank-template.xlsx**.
3. Prepping the out directory to support a newly subscribed region at a later point in time involves -
    * **Taking** a **backup** of the **existing out directory**.
    * **Copying** all the terraform **modules** and .tf files, **except** the **.auto.tfvars** and **.tfstate** files from existing region.
    * **Modifying** the **name** of **variables file** (variables_<region>.tf)
    * **Modifying** the **region parameter** in **variables_<region>.tf**
4. Preparing the out directory to support a new docker image release or update involves -
    * **Taking** a **backup** of the **existing out directory (Optional)**
    * **Copying** all the terraform **modules** and **.tf** files (Except variables_example.tf) from **/cd3user/oci_tools/cd3_automation_toolkit/user-scripts/terraform/** to region specificdirectories in out directory.

**Example:**

```
cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/terraform/
cp -R modules /cd3user/tenancies/<customer_name>/terraform_files/<region>/
cp *.tf /cd3user/tenancies/<customer_name>/terraform_files/<region>/
cd /cd3user/tenancies/<customer_name>/terraform_files/<region>/
rm -rf variables_example.tf
```
