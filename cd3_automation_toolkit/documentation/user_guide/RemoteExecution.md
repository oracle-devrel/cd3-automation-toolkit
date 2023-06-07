# Remote Execution Scenarios 

## Greenfield Tenancies (Managing Remote Execution for Green Field Tenancies)
- [Ansible Playbooks](#ansible-playbooks)
- [Shell Scripts](#shell-scripts)
- [Cloud Init Scripts](#cloud-init-scripts)


**NOTE-**
Before you start with configuring remote execution for OCI instance(s) please ensure network connectivity through Bastion host or direct reach to the OCI instance(s) from where terraform is being invoked.

Remote execution should be used as the **last resort or only during initial provisioning** for a given OCI instance(s). This feature cannot be used for export of instances.

### Ansible Playbooks
 - Add the remote_execute and bastion_ip(optional) parameters to the excel sheet for the corresponding instance entry.
 - Please skip bastion_ip if there is direct connectivity with target servers.
 - Scripts folder should have the ansible script files and ssh-keys for instances and bastion host. The *yaml/*yml extensions will be considered for the script files.
 - For block-volume attachment configuration via ansible playbook the device name is must, and it's currently set to "/dev/oracleoci/oraclevdb" in the sample ansible playbook.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Executing Terraform commands to provision the resources in OCI.
 

### Shell Scripts
 - Add the remote_execute and bastion_ip(optional) parameters to the excel sheet for the corresponding instance entry.
 - Please skip bastion_ip if there is direct connectivity with target servers.
 - Scripts folder should have the relevant shell script files and ssh-keys for instances and bastion host. The *sh extension(s) will be considered for the script files.
 - Common scenarios like security hardening and other common scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Executing Terraform commands to provision the resources in OCI.

### Cloud Init Scripts
 - Add the remote_execute param to the excel sheet for the corresponding instance entry.
 - Scripts folder should have the relevant script files and ssh-keys for instances. The *sh extension(s) will be considered for the script files.
 - Common scenarios like security hardening and other common scripts can be executed against the OCI instances during provisioning.
 - Running the CD3 automation toolkit will generate auto.tfvars.
 - Executing Terraform commands to provision the resources in OCI.


The users can refer to the ```default.yaml``` file which is inside /cd3user/tenancies/<customer_name>/terraform_files/<region>/scripts dir for provisioning the custom playbooks.

<br><br>
<div align='center'>

| <a href="/README.md#table-of-contents-bookmark">:arrow_backward: Main Menu</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/RestructuringOutDirectory.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
