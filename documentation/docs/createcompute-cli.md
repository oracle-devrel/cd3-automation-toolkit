# Provisioning Compute Instances on OCI

Provisioning of compute instances using Automation Toolkit involves the below steps:

- Add the VM details to the "Instances" Excel Sheet.
- Running the toolkit to generate auto.tfvars.
- Executing Terraform commands to provision the resources in OCI.

Note below points while adding VM details in the Instances sheet:

1. "Display Name" column is case sensitive. Specified value will be the display name of Instance in OCI console. <br>
 <br>
2. Optional columns can also be left blank - like Fault Domain, IP Address. They will take default values when left empty. <br>
 <br>
3. Leave columns: Backup Policy, NSGs, DedicatedVMHost blank if instance doesn't need to be part of any of these. Instances can be made a part of Backup Policy and NSGs later by choosing appropriate option in setUpOCI menu. <br>
 <br>

4. The column "SSH Key Var Name" accepts SSH key value directly or the name of variable declared in *variables.tf* under the  **instance_ssh_keys** variable containing the key value. Make sure to have an entry in variables_\<region>.tf file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSH key value. <br>

>For Eg: If you enter the SSH Key Var Name as **ssh_public_key**, make an entry in variables_\<region>.tf file as shown below:
 
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
    
<br>
5. Enter subnet name column value as: \<vcn-name>_\<subnet-name> <br>
<br>
6. Source Details column of the excel sheet accepts both image and boot volume as the source for instance to be launched. <br>
   Format:
   
           image::\<variable containing ocid of image> or
           bootVolume::\<variable containing ocid of boot volume>

Make sure to have an entry in variables_\<region>.tf file for the value you enter in Source Details field of the Excel sheet.
Ex: If you enter the Source Details as image::Linux, make an entry in variables_\<region>.tf file under the **instance_source_ocids** variable as shown below:


    variable 'instance_source_ocids' {
     type = map(any)
     Linux    = "<LATEST LINUX OCID HERE>"
     Windows  = "<LATEST WINDOWS OCID HERE>"
     PaloAlto = "Palo Alto Networks VM-Series Next Generation Firewall"
     #START_instance_source_ocids#
     # exported instance image ocids
     #instance_source_ocids_END#
    }
<br>
7. Mention shape to be used in Shape column of the excel sheet. If Flex shape is to be used format is:


         shape::ocpus

         eg: VM.Standard.E3.Flex::5

<br>
8. Custom Policy Compartment Name : Specify the compartment name where the Custom Policy is created. <br>
<br>
9. Create_Is PV Encryption In Transit Enabled attribute should be set to True to enable encryption for new instances. Default is False. <br>
<br>
10. Update_Is PV Encryption In Transit Enabled attribute should be set to True to enable encryption for existing instances. <br>
<br>
11. Add any additonal attributes (not part of excel sheet already) as per  [this](additional-attributes.md). <br>
<br>
12. To enable or disable a plugin for the instance add new column with name as <b>'Plugin \<plugin-name-in-console>' </b> eg 'Plugin Bastion'.
    Valid values are Enabled or Disabled <br>


## Remote Execution/Cloud Init Scenarios 
## Managing Remote Execution

**NOTE-**
Before you start with configuring remote execution for OCI instance(s) please ensure network connectivity through Bastion host or direct reach to the OCI instance(s) from where terraform is being invoked.

Remote execution should be used as the **last resort or only during initial provisioning** for a given OCI instance(s). This feature cannot be used for export of instances.

 - Add the **'Remote Execute'** columm to the excel sheet for the corresponding instance entry. Format is: bastion_ip@<scriptname> 
 - Please skip bastion_ip if there is direct connectivity with target servers via VPN.
 - Scripts folder should have the **ansible script files** or **shell script files** and ssh-keys for instances and bastion host. The *.yaml or *.yml extensions will be considered for the ansible script files and .sh extensions will be considered for shell scripts files.
 - For block-volume attachment configuration via ansible playbook the device name is must, and it's currently set to "/dev/oracleoci/oraclevdb" in the sample ansible playbook.
 - Common scenarios like security hardening and other common shell scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI. Remote executioner will also run after the instance provisioning.

 The users can refer to the ```default.yaml``` file which is inside ```/cd3user/tenancies/<customer_name>/terraform_files/<region>/scripts``` dir for provisioning the custom playbooks.
 

## Managing Cloud Init
 
 - Add the **'Cloud Init Script'** column to the excel sheet for the corresponding instance entry.
 - Scripts folder should have the relevant script files for instances. The *.sh extension(s) will be considered for the script files.
 - Common scenarios like security hardening and other common scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI and run cloud-init scripts during provisioning.


# Executing the setUpOCI.py script:

On choosing **"Compute"** in the SetUpOCI menu and **"Add/Modify/Delete Instances/Boot Backup Policy"** submenu will allow to launch your VM on OCI tenancy.

Output terraform file generated: ```<outdir>/<region>/<prefix>_instances.auto.tfvars``` and ```<outdir>/<region>/<prefix>_boot-backup-policy.auto.tfvars```  under  appropriate <region> directory.

Once the terraform apply is complete, view the resources under Compute -> Instances for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/backup_instances/<Date>-<Month>-<Time>.```



<br><br>
<div align='center'>
  
</div>
