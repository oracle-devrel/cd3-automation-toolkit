# **One Click Deployment**

This method will automatically launch the linux compute VM in OCI tenancy and configure Podman container on the VM.
<br><br>
**Prerequisites**

* The user deploying the stack should have access to launch OCI Resource Manager stack, compute instance and network resources.
!!! Example "Sample Policies"
    Allow group <group_name\> to manage orm-stacks in compartment <name\>  <br>
    Allow group <group_name\> to manage orm-jobs in compartment <name\>. <br>
    Allow group <group_name\> to manage instance-family in compartment <name\> <br>
    Allow group <group_name\> to manage virtual-network-family in compartment <name\> <br>
    
    
    
* OCI Tenancy Access as defined in [Prerequisites](prerequisites.md).
<br><br>

- [x] Click on below button to directly navigate to Resource Manager stack in the OCI Tenancy and fill in required details to launch CD3 Work VM and Container.<br>
[![Deploy_To_OCI](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-devrel/cd3-automation-toolkit/archive/refs/heads/main.zip)

- [x] This action will initiate the deployment of the Work VM in the tenancy after logging in to OCI and will configure the Automation Toolkit on a Podman container within that VM. 

- [x] Enter the required details in the Resource manager stack and click on create.
!!! Warning

    To maintain a secure environment, provide a specific source CIDR range to access the VM. Do not use 0.0.0.0/0.

!!! Note
    In case existing network is chosen to launch Work VM, it needs to have outbound internet connectivity.

- [x] After the Apply job is successful, click on it and scroll down to the end of logs and find the details for the created VM, and commands to be executed to login to the toolkit container.<br>
<img width="1124" src="../images/launch-from-stack-1.png">
<img width="1124" src="../images/launch-from-stack-2.png">
<br><br>
- [X] Login to the VM using private key corresponding to the public key provided during stack creation.
- [X] Verify if container is launched using below command - 

```
sudo podman ps -a
```
!!! Note
    If the container is still not running, wait for the stack to finish processing. You can check the logs at /cd3user/mount_path/installToolkit.log

- [X] If above command shows a running CD3 container then exec into it using below command - 

```
sudo podman exec -it cd3_toolkit bash
```

- [X] Follow [Connect CD3 Container to OCI](connect-container-to-oci-tenancy.md) for next steps. 
