# **One-Click Deployment**

This method automatically provisions a Linux compute VM in your OCI tenancy and configures the CD3 container using Podman on the instance.
<br><br>

**⚙️ Prerequisites**

* The user deploying the stack should have access to provision OCI Resource Manager stack, compute instance and network resources.
!!! Example "Sample Policies"
    Allow group <i><group_name\></i> to manage orm-stacks in compartment <i><compartment_name\></i>  <br>
    Allow group <i><group_name\></i> to manage orm-jobs in compartment <i><compartment_name\></i> <br>
    Allow group <i><group_name\></i> to manage instance-family in compartment <i><compartment_name\></i> <br>
    Allow group <i><group_name\></i> to manage virtual-network-family in compartment <i><compartment_name\></i> <br>
    
    
<br>

**🛠️ Steps:**

- [x] Click on the below button to directly navigate to Resource Manager stack in the OCI Tenancy, and fill in required details to launch CD3 Work VM and Container.<br>


    <a href="https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-devrel/cd3-automation-toolkit/archive/refs/heads/main.zip">
    <img src="https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg" alt="Deploy_To_OCI" style="height: 40px;" />
    </a>


<details>
    <summary> Alternate way to deploy the stack if above button does not work (eg for Gov tenancies) </summary>

<br>

   1.  Clone the repo using 'Download the Zip' link as highlighted below:
    <br>
	<img width="70%" height="80%"  alt="CD3 Container" src= "../images/deploystack.png"><br><br>

	
   2.   Login to OCI Console and navigate to 'Developer Services' -> 'Stacks' under 'Resource Manager' and click on 'Create Stack'. Choose .zip file and select the downloaded zip file as shown below: 
        <br>
		<img width="70%" height="80%"  alt="CD3 Container" src= "../images/rmstack.png">
</details>
		


- [x] This action initiates login to OCI, provisions the Work VM in the tenancy, and configures the Automation Toolkit within a Podman container on the VM.

- [x] Enter the required details in the Resource Manager stack and click on create.
!!! Warning "Security Warning"

    To maintain a secure environment, provide a specific source CIDR range to access the VM. Do not use 0.0.0.0/0.

!!! Note "Connectivity requirements for existing VCNs"
    In case an existing network is chosen to launch the Work VM, it needs to have outbound internet connectivity.<br>
    See <a href="../url-whitelisting"><u>URLs</u></a> that need to be whitelisted for outbound connectivity.

- [x] After the Apply job is successful, click on it and scroll down to the end of logs and find the details for the created VM, and commands to be executed to login to the toolkit container.<br>
<img width="1124" src="../images/launch-from-stack-1.png">
<img width="1124" src="../images/launch-from-stack-2.png">
<br><br>

!!! Note  "Default Security Settings"
    The VM launched using RM stack will have v1 IMDS endpoints disabled, PV encryption and the bastion plugin enabled.
- [X] Login to the VM using private key corresponding to the public key provided during stack creation. Use `cd3user` or `opc` user to connect to the VM. Same key has been copied for both the users.
- [X] Follow <a href="../cd3-cli#copy-cd3-excel-file"><u>Steps to transfer the CD3 Excel file to and from the container</u></a> while executing the toolkit.

- [X] Verify if container is launched using below command. If this command does not return any running container, wait for the stack to finish processing. The progress logs are available at `/cd3user/mount_path/installToolkit.log`

```
sudo podman ps -a
```
!!! Important " 📂 Shared Directory: VM ↔ Container"
    The path `/cd3user/mount_path/` on the VM is mapped to `/cd3user/tenancies` inside the container. This local path on VM can be used to transfer any files (Eg: Excel templates) to and from the container to the local laptop.
    

- [X] If above command shows a running CD3 container then exec into it using below command - 

```
sudo podman exec -it cd3_toolkit bash
```

- [X] Follow <a href="../connect-container-to-oci-tenancy"><u>Connect CD3 Container to OCI</u></a> for next steps. 

