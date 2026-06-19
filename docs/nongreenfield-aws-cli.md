# Export and Manage Resources from AWS (Non-Greenfield Workflow)

!!! info "Important Export behaviour"
    - Toolkit will **over-write** the data in specific tabs of CD3 Excel sheet with exported content from AWS while the other tabs remain intact.
    - Differential state import of the objects will be performed, ie the import statements will be generated only for the objects which are not already there in state file.



<span style="color: teal; font-weight: bold;">Step 1:</span>
<br>Choose the AWS CD3 Excel sheet template from <a href="../aws-excel-templates"><u>Excel Templates</u></a>
 and copy at _/cd3user/aws/<prefix\>/_<br><br>

 <b>Copy CD3 Excel File</b><br>

* While using the container launched using <a href="../launch-from-rmstack"><u>RM Stack</u></a>, local path `/cd3user/mount_path` on the VM is mapped to `/cd3user/` inside the container. So the Excel template can be copied at `/cd3user/mount_path/aws/<prefix>/` on the VM. Below is the sample command to copy the Excel template from local system to container:
```
scp -i <private key pushed to VM while creating stack> <path to excel file on local> cd3user@<Public/Private IP of the VM>:/cd3user/mount_path/aws/<prefix>
``` 

* Note that the user `cd3user` can be used to connect to the VM because same key is pushed for `opc` as well as `cd3user`.

 
<span style="color: teal; font-weight: bold;">Step 2:</span>
<br>Modify ```/cd3user/aws/<prefix>/<prefix>_setUpAWS.properties``` 
<br>Add the location of CD3 excel file under **cd3file** parameter and set **workflow_type** to **export_resources**  as shown below.
<br> The other parameters are already updated with correct values.

```ini
[Default]

# Output directory for terraform files
outdir=

# Prefix name
prefix=

# AWS authentication
aws_access_key_id=
aws_secret_access_key=


# Workflow parameters
cd3file=
workflow_type=export_resources

```
  
<br>

<span style="color: teal; font-weight: bold;">Step 3:</span>

Execute the setUpCloud.py script to start exporting the resources to CD3 and creating the terraform configuration files.

Command to Execute:
```
cd /cd3user/oci_tools/cd3_automation_toolkit/
```

```
python setUpCloud.py aws /cd3user/aws/<prefix>/<prefix>_setUpAWS.properties
```

!!! example  "Example Execution"

    [cd3user@dc6dac212f79 cd3_automation_toolkit]$ python setUpCloud.py aws /cd3user/aws/aws_demo/aws_demo_setUpAWS.properties 

    workflow_type set to export_resources. Export existing AWS objects and Synch with TF state
    We recommend to not have any existing tfvars/tfstate files for export out directory

    Choose appropriate option from below :

    1. Export DB@AWS
    <br>q. Press q to quit
    
    Enter your choice (specify comma separated to choose multiple choices):

<span style="color: teal; font-weight: bold;"><b>Expected Outputs:</b></span>

a. Excel sheet with the resource details from AWS.<br> 
b. Configuration files - <b><i>*.auto.tfvars</i></b> <br> 
c. Shell Script with import commands - <b><i>import_commands_`<resource>`.sh</i></b>



<span style="color: teal; font-weight: bold;">Step 4:</span>

Execute the <b>*import_commands_`<resource>`.sh*</b> files that are generated in the outdir.
<br>The terraform plan should show that infrastructure is up-to-date with no changes required for all regions.
  

!!! tip "Modify existing resources"
    - Once the export (including the execution of **import_commands_`<resource>`.sh**) is complete, switch the value of **workflow_type** back to **create_resources** in `<prefix>_setUpAWS.properties`. This allows the toolkit to modify these resources or create new ones on top of them.
