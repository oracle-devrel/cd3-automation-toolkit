# **Single Click Container Launch**

This will automatically launch the linux compute VM in OCI tenancy and configure Podman container on the VM.
<br><br>
**Prerequisites**

* The user deploying the stack should have access to launch OCI Resource Manager stack, compute instance and network resources.
* OCI Tenancy Access as defined in [Prerequisites](prerequisites.md).
<br><br>

- [x] Click on below button to directly navigate to Resource Manager stack in the OCI Tenancy and fill in required details to launch CD3 container.<br>
[![Deploy_To_OCI](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-devrel/cd3-automation-toolkit/archive/refs/heads/develop.zip)

- [x] This action will initiate the deployment of the Work VM in the tenancy after logging in  and will configure the Automation Toolkit on a Podman container within that VM. 

- [x] Enter the required details in the Resource manager stack and click on create.
!!! Warning
    While filling details in the stack, the recommended way is not to enable access to VM from 0.0.0.0/0 and restrict it to the specific CIDR only.

- [x] After the Apply job is successful, click on it and scroll down to the end of logs and find the details for the created VM, and commands to be executed to login to the toolkit container.<br>
<img width="1124" src="../images/launch-from-stack-1.png">
<img width="1124" src="../images/launch-from-stack-2.png">
<br><br>
- [X] Follow [Connect container to tenancy](connect-container-to-oci-tenancy.md) for next steps. 
