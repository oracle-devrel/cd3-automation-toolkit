# **Single Click Container Launch**
<br>
**Prerequisites**

* The user deploying the stack should have access to launch OCI Resource Manager stack, compute instance and network resources.
* OCI Tenancy Access as defined in [Prerequisistes](prerequisites.md).
 ---

- [x] Click on below button to directly navigate to Resource Manager stack in the OCI Tenancy and fill in required details to launch CD3 container.<br>
[![Deploy_To_OCI](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-devrel/cd3-automation-toolkit/archive/refs/heads/develop.zip)

- [x] This action will initiate the deployment of the Work VM in the tenancy and configure the Automation Toolkit on a Podman container within that VM. 
If not logged into the OCI tenancy, the button will redirect to the Oracle Cloud initial page, prompting entry of the tenancy name and login to OCI first.


- [x] Fill in the required details in the Resource manager stack and click on create. After the Apply job is successful, Click on the created Job-->Logs. Scroll down to the end and find the details for the created VM, and commands to be executed to login to the toolkit container.

!!! Caution
    While filling details in the stack, please make sure not to open access to VM from 0.0.0.0/0 and restrict it to the specific CIDR only.


- [X] Follow [Connect container to tenancy](connect-container-to-oci-tenancy.md) for next steps. 

- [X] If you plan to do set up the toolkit container in a local system, Please follow the instructions specified [here](launch-from-local.md)