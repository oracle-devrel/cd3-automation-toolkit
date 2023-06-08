# Remote Execution/Cloud Init Scenarios 

## Managing Remote Execution

**NOTE-**
Before you start with configuring remote execution for OCI instance(s) please ensure network connectivity through Bastion host or direct reach to the OCI instance(s) from where terraform is being invoked.

Remote execution should be used as the **last resort or only during initial provisioning** for a given OCI instance(s). This feature cannot be used for export of instances.

 - Add the 'Remote Execute' columm to the excel sheet for the corresponding instance entry. Format is: bastion_ip@<scriptname> 
 - Please skip bastion_ip if there is direct connectivity with target servers via VPN.
 - Scripts folder should have the **ansible script files** or **shell script files** and ssh-keys for instances and bastion host. The *.yaml or *.yml extensions will be considered for the ansible script files and .sh extensions will be considered for shell scripts files.
 - For block-volume attachment configuration via ansible playbook the device name is must, and it's currently set to "/dev/oracleoci/oraclevdb" in the sample ansible playbook.
 - Common scenarios like security hardening and other common shell scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI. Remote executioner will also run after the instance provisioning.
 

## Managing Cloud Init
 
 - Add the 'Cloud Init Script' column to the excel sheet for the corresponding instance entry.
 - Scripts folder should have the relevant script files and ssh-keys for instances. The *sh extension(s) will be considered for the script files.
 - Common scenarios like security hardening and other common scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Execute Terraform commands to provision the instances in OCI and run cloud-init scripts during provisioning.


The users can refer to the ```default.yaml``` file which is inside /cd3user/tenancies/<customer_name>/terraform_files/<region>/scripts dir for provisioning the custom playbooks.

<br><br>
<div align='center'>

| <a href="/README.md#table-of-contents-bookmark">:arrow_backward: Main Menu</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/RestructuringOutDirectory.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
