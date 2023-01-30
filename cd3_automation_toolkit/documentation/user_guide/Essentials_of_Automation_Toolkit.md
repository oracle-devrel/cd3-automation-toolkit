# **Essentials of Automation Toolkit**
There are 2 main inputs to the Automation Toolkit.
- CD3 Excel Sheet
- setUpOCI.properties

### **Excel Sheet Templates**

Below are the CD3 templates for the latest release having standardised IAM Components (compartments, groups and policies), Network Components and Events & Notifications Rules as per CIS Foundations Benchmark for Oracle Cloud.

Details on how to fill data into the excel sheet can be found in the Blue section of each sheet inside the excel file. Make appropriate changes to the templates eg region and use for deployment.

|Excel Sheet| Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Blank-template.xlsx](/cd3_automation_toolkit/example)   | 	Choose this template while exporting the existing resources from OCI into the CD3 and Terraform.| 
| [CD3-CIS-template.xlsx](/cd3_automation_toolkit/example) | This template has auto-filled in data of CIS Landing Zone for DRGv2. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases) |
|[CD3-HubSpoke-template](/cd3_automation_toolkit/example) | This template has auto-filled in data for a Hub and Spoke model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-SingleVCN-template](/cd3_automation_toolkit/example)| This template has auto-filled in data for a Single VCN model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-CIS-ManagementServices-template.xlsx](/cd3_automation_toolkit/example) | This template has auto-filled in data of CIS Landing Zone. Choose this template while creating the components of Events, Alarms, Notifications and Service Connectors|


> The Excel Templates can also be found at _/cd3user/oci_tools/cd3_automation_toolkit/example_ inside the container.

<br>Here is the CIS Landing Zone quick start template by NACE Security Team also: https://www.ateam-oracle.com/cis-oci-landing-zone-quickstart-template


### **setUpOCI.properties**

**Current Version:  setUpOCI.properties v10**

Make sure to use/modify the properties file at _/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ during executions.

```
[Default]

#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_name>/terraform_files
outdir=/cd3user/tenancies/<customer_name>/terraform_files

#prefix for output terraform files eg customer name like demotenancy
prefix=

#input config file for Python API communication with OCI eg example\config;
config_file=

#path to cd3 excel eg /cd3user/tenancies/<customer_name>\CD3-Customer.xlsx
cd3file=

#Is it Non GreenField tenancy
non_gf_tenancy=false
```

| Variable | Description | Example |
|---|---|---|
|outdir|Path to output directory where terraform files will be generated| /cd3user/tenancies/<customer\_name> /terraform\_files|
|prefix|Prefix for output terraform files|\<customer\_name>|
|config\_file|Python config file|/cd3user/tenancies/<customer\_name>/config|
| cd3file |Path to the CD3 input file |/cd3user/tenancies/<customer\_name>/testCD3. xlsx |
|non\_gf\_tenancy |Specify if its a Non Green field tenancy or not (**True** or **False**)| False|

<blockquote>For more information on usage of non_gf_tenancy flag, refer to <a href = /cd3_automation_toolkit/documentation/user_guide/Workflows.md> Automation Toolkit Workflows</a></blockquote>

### **Execution Steps Overview:**
Choose the appropriate CD3 Excel Sheet and update the setUpOCI.properties file at _/cd3user/tenancies/<customer\_name>/<customer\_name>\_setUpOCI.properties_ and run the commands below:

**Step 1**:
<br>Change Directory to 'cd3_automation_toolkit'
<br>```cd /cd3user/oci_tools/cd3_automation_toolkit/```

**Step 2**:
<br>Place Excel sheet at appropriate location in your container and provide the corresponding path in _cd3file_ parmeter of: _/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ file

**Step 3**
<br>
Execute the setUpOCI Script:                                                                                                                                           <br>```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
<br> → Example execution of the script:

```
[cd3user@25260a87b137 cd3_automation_toolkit]$ python setUpOCI.py /cd3user/tenancies/demotenancy/demotenancy_setUpOCI.properties
Updated OCI_Regions file !!!
Script to fetch the compartment OCIDs into variables file has not been executed.
Do you want to run it now? (y|n):
```
→ This prompt appears for the very first time when you run the toolkit or when any new compartments are created using the toolkit. Enter 'y' to fetch the details of compartment OCIDs into variables file.
<br>→ After fetching the compartment details, the toolkit will display the menu options.

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>

