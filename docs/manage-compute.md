## Create New Compute Instances in OCI(Greenfield Workflow)

Provisioning of compute instances using Automation Toolkit involves the below steps:

- Adding the VM details to the "Instances" Excel Sheet.
- Updating the ```/cd3user/tenancies/<prefix>/terraform_files/<region>/<service_dir>/variables_<region>.tf``` file with information about ssh key, source ocid. 
- Running the toolkit with 'Create Resources' workflow to generate *.auto.tfvars.
- Executing Terraform/Tofu to provision the resources in OCI.

**1. Update Excel Sheet**

- "Display Name" column is case sensitive. Specified value will be the display name of Instance in OCI console. <br>

- Optional columns can also be left blank - like Fault Domain, IP Address. They will take default values when left empty. <br>

- Leave columns: Backup Policy, NSGs, DedicatedVMHost blank if instance doesn't need to be part of any of these. Instances can be made a part of Backup Policy and NSGs later by choosing appropriate option in setUpOCI menu. <br>

- Enter subnet name column value as: ```<network-compartment-name>@<vcn-name>::<subnet-name>``` <br>

- Create_Is PV Encryption In Transit Enabled attribute should be set to True to enable encryption for new instances. Default is False. <br>

- Update_Is PV Encryption In Transit Enabled attribute should be set to True to enable encryption for existing instances. <br>

- Add any additional attributes (not part of excel sheet already) <a href="../additional-attributes"><u>following this link</u></a>. <br>

- To enable or disable a plugin for the instance add new column with name as ```Plugin <plugin-name-in-console>``` eg 'Plugin Bastion'.
    Valid values are Enabled or Disabled <br>
- Mention shape to be used in Shape column of the excel sheet. If Flex shape is to be used format is: ```shape::ocpus``` eg ```VM.Standard.E3.Flex::5```


- Custom Policy Compartment Name: Specify the compartment name where the Custom Policy is created.

<u>Managing Remote Execution</u>

!!! note 
    Before configuring remote execution for OCI instance(s), ensure network connectivity through Bastion host or direct reach to the OCI instance(s) from where terraform is being invoked.

Remote execution should be used as the _last resort or only during initial provisioning_ for a given OCI instance(s). This feature cannot be used for export of instances.

 - Add the _'Remote Execute'_ columm to the excel sheet for the corresponding instance entry. Format is: bastion_ip@<scriptname> 
 - Skip bastion_ip if there is direct connectivity with target servers via VPN.
 - Scripts folder should have the _ansible script files_ or _shell script files_ and ssh-keys for instances and bastion host. The *.yaml or *.yml extensions will be considered for the ansible script files and .sh extensions will be considered for shell scripts files.
 - For block-volume attachment configuration via ansible playbook the device name is must, and it's currently set to _"/dev/oracleoci/oraclevdb"_ in the sample ansible playbook.
 - Common scenarios like security hardening and other common shell scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform/Tofu commands to provision the instances in OCI. Remote executioner will also run after the instance provisioning.

 The users can refer to the ```default.yaml``` file which is inside ```/cd3user/tenancies/<prefix>/terraform_files/<region>/<service_dir>/scripts``` dir for provisioning the custom playbooks.
 

<u>Managing Cloud Init</u>
 
 - Add the _'Cloud Init Script'_ column to the excel sheet for the corresponding instance entry.
 - Scripts folder should have the relevant script files for instances. The *.sh extension(s) will be considered for the script files.
 - Common scenarios like security hardening and other common scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI and run cloud-init scripts during provisioning.


**2. Update variables_<region\>.tf**

- Location of the file - ```/cd3user/tenancies/<prefix>/terraform_files/<region>/<service_dir>/variables_<region>.tf```
- The "SSH Key Var Name" column accepts either the SSH key value directly or the name of a variable declared in variables.tf under the **instance_ssh_keys** variable that contains the key value. Ensure there is an entry in the variables_<region\>.tf file with the name entered in the SSH Key Var Name field of the Excel sheet, and set the value to the SSH key value.

    !!! Example
        If the SSH Key Var Name is entered as **ssh_public_key** in the Excel sheet, make an entry in the variables_<region\>.tf file as shown below.
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

- Source Details column of the excel sheet accepts both image and boot volume as the source for instance to be launched. <br>
        ```   
        image::\<variable containing ocid of image> or
        bootVolume::\<variable containing ocid of boot volume>. 
        ```
Ensure there is an entry in the variables_<region\>.tf file for the value entered in the Source Details field of the Excel sheet.

    !!! Example
          If the source details is entered as **image::Linux**, an entry should be made in the variables_<region\>.tf file under the **instance_source_ocids** variable as shown below:
    ```
    variable 'instance_source_ocids' {
     type = map(any)
     Linux    = "<LATEST LINUX OCID HERE>"
     Windows  = "<LATEST WINDOWS OCID HERE>"
     PaloAlto = "Palo Alto Networks VM-Series Next Generation Firewall"
     #START_instance_source_ocids#
     # exported instance image ocids
     #instance_source_ocids_END#
    }
    ```
    !!! Important
        Execute GIT commands to sync these variables_<region\>.tf file changes  with DevOps GIT Repo in case **toolkit is being used with Jenkins,** <a href="../sync-cli-jenkins"><u>Here are the Steps</u></a>.

**3.  Execute setUpOCI and terraform/tofu apply**

On choosing _"Compute"_ in the SetUpOCI menu and _"Add/Modify/Delete Instances/Boot Backup Policy"_ submenu will allow to launch the VM on OCI tenancy.

Output tfvars file generated: ```<outdir>/<region_dir>/<service_dir><prefix>_instances.auto.tfvars``` and ```<outdir>/<region_dir>/<service_dir>/<prefix>_boot-backup-policy.auto.tfvars```  

Once the terraform/tofu apply is complete, view the resources under Compute -> Instances for the region.

Upon re-running the same option, the previously existing files will be backed up under the directory →   ```<outdir>/<region_dir>/<service_dir>/backup_instances/<Date>-<Month>-<Time>.```

## Export Existing Compute Resources from OCI (Non-Greenfield Workflow)


1. Use the <a href="https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example"><u>CD3-Blank-Template.xlsx</u></a> to export existing OCI VM details into the "Instances" sheet. <br>

2. <a href="../additional-attributes"><u>Add any additional attributes</u></a> (not part of excel sheet already) which needs to be exported . <br>

3. Make sure to export the VCNs and Subnets in which the Instances are present prior to exporting the Instance. <br>

4. Execute the _setupOCI_ with _Workflow Type_ as _Export Resources_ <br>
   ```
   python setUpOCI.py /cd3user/tenancies/<prefix>/<prefix>_setUpOCI.properties
``` 
5. Provide the region from where the Instances have to be exported. Specify comma separated values for multiple regions. <br>

6. From the output menu, select **Export Compute >> Export Instances**. <br>

7. Enter the compartment to which the Instances belong to. When exporting instances from multiple compartments, specify the compartment values as comma-separated values. <br>
Specify the compartment name along with hierarchy in the below format:

        Parent Compartment1::Parent Compartment2::MyCompartment 
 

8. To export only specific instances, specify the required filter values
     - Enter comma separated list of display name patterns of the instances: 
     - Enter comma separated list of ADs of the instances eg AD1,AD2,AD3: <br>


9. Upon executing, the "Instances" sheet in input CD3 Excel is populated with the VMs details. <br>

10. The *import_commands_instances.sh* script, tfvars file are generated for the Instances under folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>```. <br>

11. The associated ssh public keys are placed under variables_<region\>.tf under the "instance_ssh_keys" variable.  <br>

12. While export of instances, it will fetch details for only the primary VNIC attached to the instance. <br>

13. Execute the .sh file (*sh import_commands_instances.sh*) to generate terraform state file. <br>  **This will be automatically executed while using the toolkit with Jenkins.**

14. Check out the <a href="../knownbehaviour"><u>known behaviour of toolkit</u></a> for export of instances having multiple plugins.



