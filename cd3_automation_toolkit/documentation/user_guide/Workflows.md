# Using the Automation Toolkit via CLI

### **Prepare setUpOCI.properties**
**Current Version:  setUpOCI.properties v2024.1.0**

Make sure to use/modify the properties file at _/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ during executions.

```ini
[Default]

#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_name>/terraform_files
outdir=

#prefix for output terraform files eg <customer_name> like demotenancy
prefix=

# auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=

#input config file for Python API communication with OCI eg /cd3user/tenancies/<customer_name>/.config_files/<customer_name>_config;
config_file=

# Leave it blank if you want single outdir or specify outdir_structure_file.properties containing directory structure for OCI services.
outdir_structure_file=

#path to cd3 excel eg /cd3user/tenancies/<customer_name>\CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in OCI(greenfield workflow)
#specify export_resources to export resources from OCI(non-greenfield workflow)
workflow_type=create_resources
```

| Variable | Description | Example |
|---|---|---|
|outdir|Path to output directory where terraform files will be generated| /cd3user/tenancies/<customer\_name>/terraform\_files|
|prefix|Prefix for output terraform files|\<customer\_name>|
|auth_mechanism|Authentication Mechanism for OCI APIs|api_key|
|config\_file|Python config file|/cd3user/tenancies/<customer\_name>/.config_files/<customer\_name>_config|
|outdir\_structure\_file |Parameter specifying single outdir or different for different services|Blank or <customer\_name>_outdir_structure_file.properties|
| cd3file |Path to the Excel input file |/cd3user/tenancies/<customer\_name>/testCD3. xlsx |
|workflow\_type |greenfield workflow or non-greenfield workflow| See <a href = /cd3_automation_toolkit/documentation/user_guide/Workflows.md#automation-toolkit-workflows> Automation Toolkit Workflows</a> for more information|


### **Automation Toolkit Workflows:**
CD3 Automation Tool Kit supports 2 main workflows:
1.	<a href="/cd3_automation_toolkit/documentation/user_guide/GreenField.md">Create Resources in OCI (Greenfield Workflow)</a> - Empty OCI tenancy (or) do not need to modify / use any existing resources.
2.	<a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField.md">Export Resources from OCI (Non-Greenfield Workflow)</a> - Need to use / manage existing resources.  Export existing resources into CD3 & TF State, then use the Greenfield workflow.



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

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows-jenkins.md">:arrow_backward: Automation Toolkit via Jenkins</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>

