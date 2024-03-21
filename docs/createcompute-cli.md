# Provisioning Compute Instances in OCI

Provisioning of compute instances using Automation Toolkit involves the below steps:

- Add the VM details to the "Instances" Excel Sheet.
- Running the toolkit to generate auto.tfvars.
- Executing Terraform commands to provision the resources in OCI.

## Important Notes
Note below points while adding VM details in the Instances sheet:

1. "Display Name" column is case sensitive. Specified value will be the display name of Instance in OCI console. <br>

2. Optional columns can also be left blank - like Fault Domain, IP Address. They will take default values when left empty. <br>

3. Leave columns: Backup Policy, NSGs, DedicatedVMHost blank if instance doesn't need to be part of any of these. Instances can be made a part of Backup Policy and NSGs later by choosing appropriate option in setUpOCI menu. <br>


4. The "SSH Key Var Name" column accepts either the SSH key value directly or the name of a variable declared in variables.tf under the **instance_ssh_keys** variable that contains the key value. Ensure there is an entry in the variables_<region\>.tf file with the name entered in the SSH Key Var Name field of the Excel sheet, and set the value to the SSH key value.
 <br>

!!! quote "Example"
    If the SSH Key Var Name is entered as **ssh_public_key** in the Excel sheet, make an entry in the variables_<region>.tf file as shown below.
```
    variable  'instance_ssh_keys'  {
    type = map(any)
    default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    # Use '\n' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
    #START_instance_ssh_keys#
    # exported instance ssh keys
    #instance_ssh_keys_END#
      }
    } 
```

<br>

5. Enter subnet name column value as: <vcn-name\>_<subnet-name\> <br>

6. Source Details column of the excel sheet accepts both image and boot volume as the source for instance to be launched. <br>
   Format:
   
           image::\<variable containing ocid of image> or
           bootVolume::\<variable containing ocid of boot volume>

Ensure there is an entry in the variables_<region\>.tf file for the value entered in the Source Details field of the Excel sheet.

For example, If the source details is entered as **image::Linux**, an entry should be made in the variables_<region\>.tf file under the **instance_source_ocids** variable as shown below:

    variable 'instance_source_ocids' {
     type = map(any)
     Linux    = "<LATEST LINUX OCID HERE>"
     Windows  = "<LATEST WINDOWS OCID HERE>"
     PaloAlto = "Palo Alto Networks VM-Series Next Generation Firewall"
     #START_instance_source_ocids#
     # exported instance image ocids
     #instance_source_ocids_END#
    }

7. Mention shape to be used in Shape column of the excel sheet. If Flex shape is to be used format is:


         shape::ocpus
         eg: VM.Standard.E3.Flex::5


8. Custom Policy Compartment Name : Specify the compartment name where the Custom Policy is created. <br>

9. Create_Is PV Encryption In Transit Enabled attribute should be set to True to enable encryption for new instances. Default is False. <br>

10. Update_Is PV Encryption In Transit Enabled attribute should be set to True to enable encryption for existing instances. <br>

11. Add any additonal attributes (not part of excel sheet already) as per  [this](additional-attributes.md). <br>

12. To enable or disable a plugin for the instance add new column with name as <b>'Plugin <plugin-name-in-console\>' </b> eg 'Plugin Bastion'.
    Valid values are Enabled or Disabled <br>


## Remote Execution/Cloud Init Scenarios 
**Managing Remote Execution**

!!! note 
    Before configuring remote execution for OCI instance(s), ensure network connectivity through Bastion host or direct reach to the OCI instance(s) from where terraform is being invoked.

Remote execution should be used as the _last resort or only during initial provisioning_ for a given OCI instance(s). This feature cannot be used for export of instances.

 - Add the _'Remote Execute'_ columm to the excel sheet for the corresponding instance entry. Format is: bastion_ip@<scriptname> 
 - Skip bastion_ip if there is direct connectivity with target servers via VPN.
 - Scripts folder should have the _ansible script files_ or _shell script files_ and ssh-keys for instances and bastion host. The *.yaml or *.yml extensions will be considered for the ansible script files and .sh extensions will be considered for shell scripts files.
 - For block-volume attachment configuration via ansible playbook the device name is must, and it's currently set to _"/dev/oracleoci/oraclevdb"_ in the sample ansible playbook.
 - Common scenarios like security hardening and other common shell scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI. Remote executioner will also run after the instance provisioning.

 The users can refer to the ```default.yaml``` file which is inside ```/cd3user/tenancies/<customer_name>/terraform_files/<region>/scripts``` dir for provisioning the custom playbooks.
 

**Managing Cloud Init**
 
 - Add the _'Cloud Init Script'_ column to the excel sheet for the corresponding instance entry.
 - Scripts folder should have the relevant script files for instances. The *.sh extension(s) will be considered for the script files.
 - Common scenarios like security hardening and other common scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI and run cloud-init scripts during provisioning.


## Executing the setUpOCI.py script:

On choosing _"Compute"_ in the SetUpOCI menu and _"Add/Modify/Delete Instances/Boot Backup Policy"_ submenu will allow to launch the VM on OCI tenancy.

Output terraform file generated: ```<outdir>/<region_dir>/<service_dir><prefix>_instances.auto.tfvars``` and ```<outdir>/<region_dir>/<service_dir>/<prefix>_boot-backup-policy.auto.tfvars```  

Once the terraform apply is complete, view the resources under Compute -> Instances for the region.

Upon re-running the same option, the previously existing files will be backed up under the directory →   ```<outdir>/<region_dir>/<service_dir>/backup_instances/<Date>-<Month>-<Time>.```



<br><br>
<div align='center'>
  
</div>
