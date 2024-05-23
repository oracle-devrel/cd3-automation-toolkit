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

<details>
    <summary> Alternate way to deploy the stack if above button does not work (eg for Gov tenancies) </summary>

    <br>
    - Clone the repo using 'Download the Zip' link as shown below:<br>

		<img width="70%" height="80%"  alt="CD3 Container" src= "../images/deploystack.png"><br><br>

	
    - Login to OCI Console and navigate to 'Developer Services' -> Stacks under 'Resource Manager' and click on Create Stack. Chose .zip file and select the downloaded zip file as shown below: <br>
		<img width="70%" height="80%"  alt="CD3 Container" src= "../images/rmstack.png">
</details>
		


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
- [X] Login to the VM using private key corresponding to the public key provided during stack creation. Use 'cd3user' or 'opc' user to connect to the VM. Same key has been copied for both the users.
- [X] Follow [these](cd3-cli.md#copy-cd3-excel-file) to copy the excel file to and from the container while executing the toolkit.
- [X] Verify if container is launched using below command. If this command does not return any running container, wait for the stack to finish processing. The progress logs are available at /cd3user/mount_path/installToolkit.log

```
sudo podman ps -a
```
!!! Important
    Path /cd3user/mount_path/ on the VM is mapped to /cd3user/tenancies inside the container. This local path on VM can be used to transfer any data to and from the container to the local laptop.
    

- [X] If above command shows a running CD3 container then exec into it using below command - 

```
sudo podman exec -it cd3_toolkit bash
```

- [X] Follow [Connect CD3 Container to OCI](connect-container-to-oci-tenancy.md) for next steps. 
