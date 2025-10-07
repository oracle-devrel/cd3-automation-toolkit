# Export and Manage Resources from Azure (Non-Greenfield Workflow)

!!! info "Important Export behaviour"
    - Toolkit will **over-write** the data in specific tabs of CD3 Excel sheet with exported content from Azure while the other tabs remain intact.
    - Differential state import of the objects will be performed, ie the import statements will be generated only for the objects which are not already there in state file.



<span style="color: teal; font-weight: bold;">Step 1:</span>
<br>Choose the Azure CD3 Excel sheet template from <a href="../az̄r-excel-templates"><u>Excel Templates</u></a>
 and copy at _/cd3user/azure/<prefix\>/_<br><br>

 
<span style="color: teal; font-weight: bold;">Step 2:</span>
<br>Modify ```/cd3user/azure/<prefix>/<prefix>_setUpAzure.properties``` 
<br>Add the location of CD3 excel file under **cd3file** parameter and set **workflow_type** to **export_resources**  as shown below.
<br> The other parameters are already updated with correct values.

```ini
[Default]

#Input variables required to run setUpAzure script

#path to output directory where terraform file will be generated. eg /cd3user/azure/<prefix>/terraform_files
outdir=

#prefix for output terraform files eg demo
prefix=

# Auth Params
subscription_id=

tenant_id=

client_id=

client_secret=

#path to cd3 excel eg /cd3user/azure/<prefix>\CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in Azure(greenfield workflow)
#specify export_resources to export resources from Azure(non-greenfield workflow)
workflow_type=create_resources
```
  
<br>

<span style="color: teal; font-weight: bold;">Step 3:</span>

Execute the setUpCloud.py script to start exporting the resources to CD3 and creating the terraform configuration files.

Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```

```
python setUpCloud.py azure /cd3user/azure/<prefix>/<prefix>_setUpAure.properties
```

!!! example  "Example Execution"

    [cd3user@dc6dac212f79 cd3_automation_toolkit]$ python setUpCloud.py azure /cd3user/azure/az_demo/az_demo_setUpAzure.properties 

    workflow_type set to export_resources. Export existing Azure objects and Synch with TF state
    We recommend to not have any existing tfvars/tfstate files for export out directory

    Choose appropriate option from below :

    1. Export DB @Azure
    <br>q. Press q to quit
    
    Enter your choice (specify comma separated to choose multiple choices):

<span style="color: teal; font-weight: bold;"><b>Expected Outputs:</b></span>

a. Excel sheet with the resource details from Azure.<br> 
b. Configuration files - <b><i>*.auto.tfvars</i></b> <br> 
c. Shell Script with import commands - <b><i>import_commands_`<resource>`.sh</i></b>



<span style="color: teal; font-weight: bold;">Step 4:</span>

Execute the <b>*import_commands_`<resource>`.sh*</b> files that are generated in the outdir.
<br>The terraform plan should show that infrastructure is up-to-date with no changes required for all regions.
  

!!! tip "Modify existing resources"
    - Once the export (including the execution of **import_commands_`<resource>`.sh**) is complete, switch the value of **workflow_type** back to **create_resources** in `<prefix>_setUpAzure.properties`. This allows the toolkit to modify these resources or create new ones on top of them.
