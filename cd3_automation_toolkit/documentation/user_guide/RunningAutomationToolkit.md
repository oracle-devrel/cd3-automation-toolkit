# **Running the Automation Toolkit**

Once the previous script createTenancyConfig.py has been run successfully, next step is to choose the appropriate CD3 Excel Sheet and update the setUpOCI.properties file at /cd3user/tenancies/<customer\_name>/<customer\_name>\_setUpOCI.properties. Finally, run the commands displayed in the console output. These commands are also made available in the cmds.log file of the output directory for future reference.

## **Excel Sheet Templates - CIS Landing Zone**

Below are the CD3 templates for the latest release having standardised IAM Components (compartments, groups and policies), Network Components and Events & Notifications Rules as per CIS Landing Zone and the CIS Foundations Benchmark for Oracle Cloud.

Details on how to fill the data into the excel sheet can be found in the Blue section of each sheet inside the excel file. Please refer CD3 Excel Information for additional details on each tab of the excel sheets.

**Excel Sheet Purpose!**

|Excel Sheet| Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Blank-template.xlsx](/cd3-automation-toolkit/cd3_automation_toolkit/example/CD3-Blank-template.xlsx)   | 	Choose this template while exporting the existing resources to the CD3 and Terraform.| 
| [CD3-CIS-template.xlsx](/cd3-automation-toolkit/cd3_automation_toolkit/example/CD3-CIS-template.xlsx) | This template has auto-filled in data of CIS Landing Zone. Choose this template while using a tenancy that supports DRGV2. |
|[CD3-HubSpoke-template](/cd3-automation-toolkit/cd3_automation_toolkit/example/CD3-HubSpoke-template.xlsx) | This template has auto-filled in data for a Hub and Spoke model of networking. The user must only modify the region according to requirement and execute the toolkit to generate the terraform files.|
|[CD3-CIS-ManagementServices-template.xlsx](/cd3-automation-toolkit/cd3_automation_toolkit/example/CD3-CIS-ManagementServices-template.xlsx) | This template has auto-filled in data of CIS Landing Zone. Choose this template while creating the components of Events, Alarms and Notifications.|
|[CD3-SingleVCN-template](/cd3-automation-toolkit/cd3_automation_toolkit/example/CD3-SingleVCN-template.xlsx)| This template has auto-filled in data for a Single VCN model of networking. The user must only modify the region xlsx  according to requirement and execute the toolkit to generate the terraform files.|

Here is the CIS Landing Zone quick start template by NACE Security Team also: https://www.ateam-oracle.com/cis-oci-landing-zone-quickstart-template


> The Excel Templates can also be found at /cd3user/oci_tools/cd3_automation_toolkit/example inside the container.


## **setUpOCI.properties**

Before we start with the steps to execute the Automation Toolkit, kindly update the properties file which is the input to the Toolkit. 

**Current Version:  setUpOCI.properties v10**

Example File: (This file can be found at /cd3user/oci\_tools/cd3\_automation\_toolkit/. Make sure to use/modify the properties file at /cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties during executions)

```
[Default]
 
#Input variables required to run setUpOCI script
#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_tenancy_name>/terraform_files when running from cd3toolkit docker container 
outdir=/cd3user/tenancies/demotenancy/terraform_files

#prefix for output terraform files eg client name prefix=demotenancy
prefix=

#input config file for Python API communication with OCI eg example\config; Leave it blank if code is being executed from OCS Work VM
config_file=

#params required if input data format is cd3
#path to cd3 excel eg example\CD3-template.xlsx cd3file=/cd3user/tenancies/demotenancy/CD3-demotenancy-template.xlsx
cd3file=

#Is it a Non Green Field tenancy 
non_gf_tenancy=false
```

| Variable | Description | Example |
|---|---|---|
|outdir|Path to output directory where terraform files will be generated| /cd3user/tenancies/<customer\_name> /terraform\_files|
|prefix|Prefix for output terraform files|\<customer\_name>|
|config\_file|Python config file|/cd3user/tenancies/<customer\_name>/config|
| cd3file |Path to the CD3 input file |/cd3user/tenancies/<customer\_name>/testCD3. xlsx |
|non\_gf\_tenancy |Specify if its a Non Green field tenancy or not (**True** or **False**)| False|

**Execution Steps:**

| Steps                                                                                                                                                                                        | Command |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| Change Directory to that of cd3_automation_toolkit                                                                                                                                           | ```cd /cd3user/oci_tools/cd3_automation_toolkit/```|
| Edit the setUpOCI.properties at location: __/cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties__ with appropriate values.                                                | Place Excel sheet at appropriate location in your docker and provide the corresponding path in: /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties__ file |
| Execute the setUpOCI Script                                                                                                                                                                  | ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties``` |
| **Additional Information**: Execute the command to fetch the details of the compartments if it already exists/created in OCI. These details will be written to the terraform variables file. | Choose **"Fetch Compartments OCIDs to variables file"** from CD3 Services in setUpOCI menu.|

Choose the right option by setting the property non_gf_tenancy of setUpOCI.properties , to toggle between the two workflows:
1. Set the property **non_gf_tenancy**  to **false** for supporting **Green Field Tenancies** 

    →  this will help to **create** new resources
2. Set the property  **non_gf_tenancy**  to **true** for supporting  **Non - Green Field Tenancies**

    →  this will help to **export** existing resources **from OCI to CD3**,

    →  create the terraform configuration files for them and 

    →  a shell script containing the import commands to import the state of exported components to the tfstate file.

   
   Once the export (including the execution of **tf_import_commands_<resource>_nonGF.sh**) is complete, switch the value of **non_gf_tenancy** back to **false**. 


   This allows the Tool Kit to support the tenancy as Green Field from this point onwards.

