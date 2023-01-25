## **Running the Automation Toolkit**

Once the previous script 'createTenancyConfig.py' has been run successfully, next step is to choose the appropriate CD3 Excel Sheet and update the setUpOCI.properties file at /cd3user/tenancies/<customer\_name>/<customer\_name>\_setUpOCI.properties. Finally, run the commands displayed in the console output of the previous script. These commands are also made available in the cmds.log file of the output directory for future reference.

### **Excel Sheet Templates**

Below are the CD3 templates for the latest release having standardised IAM Components (compartments, groups and policies), Network Components and Events & Notifications Rules as per CIS Foundations Benchmark for Oracle Cloud.

Details on how to fill the data into the excel sheet can be found in the Blue section of each sheet inside the excel file. Make appropriate changes to the templates eg region and use them as is for deployment.

|Excel Sheet| Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Blank-template.xlsx](/cd3_automation_toolkit/example)   | 	Choose this template while exporting the existing resources from OCI into the CD3 and Terraform.| 
| [CD3-CIS-template.xlsx](/cd3_automation_toolkit/example) | This template has auto-filled in data of CIS Landing Zone for DRGv2. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases) |
|[CD3-HubSpoke-template](/cd3_automation_toolkit/example) | This template has auto-filled in data for a Hub and Spoke model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-SingleVCN-template](/cd3_automation_toolkit/example)| This template has auto-filled in data for a Single VCN model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-CIS-ManagementServices-template.xlsx](/cd3_automation_toolkit/example) | This template has auto-filled in data of CIS Landing Zone. Choose this template while creating the components of Events, Alarms, Notifications and Service Connectors|


> The Excel Templates can also be found at /cd3user/oci_tools/cd3_automation_toolkit/example inside the container.

<br>Here is the CIS Landing Zone quick start template by NACE Security Team also: https://www.ateam-oracle.com/cis-oci-landing-zone-quickstart-template


### **setUpOCI.properties**

Before we start with the steps to execute the Automation Toolkit, kindly update the properties file which is the input to the Toolkit. 

**Current Version:  setUpOCI.properties v10**

Make sure to use/modify the properties file at /cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties during executions

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

**More information about non_gf_tenancy flag:**
1. Set the property **non_gf_tenancy**  to **false** for supporting **Green Field Tenancies** 

    →  this will help to **create** new resources
2. Set the property  **non_gf_tenancy**  to **true** for supporting  **Non - Green Field Tenancies**

    →  this will help to **export** existing resources **from OCI to CD3**,

    →  create the terraform configuration files for them and 

    →  a shell script containing the import commands to import the state of exported components to the tfstate file.

   
   Once the export (including the execution of **tf_import_commands_`<resource>`_nonGF.sh**) is complete, switch the value of **non_gf_tenancy** back to **false**. 


   This allows the Tool Kit to support the tenancy as Green Field from this point onwards.

### **Execution Steps:**
**Step 1**:
<br>Change Directory to 'cd3_automation_toolkit'
<br>```cd /cd3user/oci_tools/cd3_automation_toolkit/```

**Step 2**:
<br>Place Excel sheet at appropriate location in your container and provide the corresponding path _cd3file_ parmeter of: /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties file

**Step 3**
<br>Execute the command to fetch the details of the compartments if it already exists/created in OCI. These details will be written to the terraform variables file. Choose **"Fetch Compartments OCIDs to variables file"** from CD3 Services in setUpOCI menu.

**Step 4**
<br>
Execute the setUpOCI Script:                                                                                                                                           <br>```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```



