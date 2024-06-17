# Clone OCI Environments across Tenancies using CD3 automation toolkit through Jenkins Pipelines

## Introduction

ISVs or System Integrators or Partners often encounter a typical situation while cloning OCI Resources from one environment (Tenancy/Compartment/Region) to another environment. It takes few days/months to clone the whole infrastructure manually, which can be achieved seamlesly using CD3 automation toolkit within minutes

CD3 stands for Cloud Deployment Design Deliverable. The CD3 Automation toolkit enables you to effortlessly Build, Export and Manage OCI (Oracle Cloud Infrastruture) resources by converting Excel templates to fully functional Terraform modules within minutes. Please click [here](https://oracle-devrel.github.io/cd3-automation-toolkit/cd3-overview/) to know more about CD3 automation toolkit.

## Objectives
   • Clone or Export OCI infrastructure in one environment (Tenancy/Compartment/Region) to another environment using Cloud Deployment Design Deliverable (CD3) automation toolkit through Jenkins Pipelines

## Prerequisites
   • Oracle Cloud Infrastructure Identity and Access Management (OCI IAM) policy to allow user to manage the services that are required to be exported/created using CD3 automation toolkit

   • The user executing the CD3 should have access to launch OCI Resource Manager stack, atleast **READ** access in Source OCI Tenancy and **Manage** Access for required OCI resources (Compute, Network, Storage, etc.) in Target OCI Tenancy

   • Set up **2 Compute Instances (Work VM)** on OCI and connect one Work VM to Source OCI Tenancy and other to Target OCI Tenancy. Please follow the steps below to deploy the Work VMs and connect to OCI Tenancies.

   • A beginner level of understanding of Jenkins is required

!!! **Important**
    Ensure to have required service limits in the target environment before cloning

## Deployment of Work VM using OCI Resource Manager Stack

OCI Resource Manager Stack will automatically launch the a linux compute VM in OCI tenancy and configure Podman container on the VM.

1. Click on below button to directly navigate to OCI Resource Manager stack and fill in required details to launch CD3 Work VM & Container.<br>
[![Deploy_To_OCI](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-devrel/cd3-automation-toolkit/archive/refs/heads/main.zip)

2. This action will initiate the deployment of the Work VM in the tenancy after logging in to OCI and will configure the Automation Toolkit on a Podman container within that Work VM. 

3. Enter the required details in the Resource manager stack and click on **Create**

4. After the Apply job is successful, click on it and scroll down to the end of logs and find the details for the created VM, and commands to be executed to login to the toolkit container
5. Login to the VM using private key corresponding to the public key provided during stack creation. Use 'cd3user' or 'opc' user to connect to the VM. Same key has been copied for both the users
6. Please use scp command to copy the excel file to and from the container while executing the toolkit. Below is an example of copying excel file to Work VM
```
scp -i <privaye key pushed to VM while creating stack> <path to excel file on local> cd3user@<Public/Private IP of the VM>:/cd3user/mount_path/<customer_name>
```
7. Verify if container is launched using below command. If this command does not return any running container, wait for the stack to finish processing. The progress logs are available at /cd3user/mount_path/installToolkit.log
```
sudo podman ps -a
```
8. If above command shows a running CD3 container then exec into the container using below command
```
sudo podman exec -it cd3_toolkit bash

```
!!! Important
    Path /cd3user/mount_path/ on the Work VM is mapped to /cd3user/tenancies inside the container. This local path on Work VM can be used to transfer any data to and from the container to the local laptop
## Connect container to OCI Tenancy

1. Login to the Container using ```sudo podman exec -it cd3_toolkit bash```
2. Choose preferred Authentication Mechanism for OCI SDK

     - Click [here](authmechanisms.md) to configure any one of the available authentication mechanisms.
  
3. Edit **tenancyconfig.properties**

4. Change the Directory to below 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/
  ```

5. Fill/Update the input parameters in ```tenancyconfig.properties``` file.


 **_tenancyconfig.properties_**

<details>
    <summary> Parameter Description </summary>
    <table>
        <tr>
            <th>Parameter</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>customer_name</td>
            <td>Friendly name for the Customer Tenancy</td>
            <td>demo</td>
        </tr>
        <tr>
            <td>tenancy_ocid</td>
            <td>OCID of the tenancy</td>
            <td>ocid1.tenancy.oc1..aaaaaa...5t</td>
        </tr>
        <tr>
            <td>region</td>
            <td>OCI Region identifier</td>
            <td>us-phoenix-1</td>
        </tr>
        <tr>
            <td>auth_mechanism</td>
            <td>Auth Mechanism for OCI APIs</td>
            <td>api_key, instance_principal, session_token</td>
        </tr>
        <tr>
            <td>user_ocid</td>
            <td>Required only if ${auth_mechanism} is selected as api_key. Leave empty if 'instance_principal' or 'session_token' is used</td>
            <td>ocid1.user.oc1..aaaaa...6a</td>
        </tr>
        <tr>
            <td>key_path</td>
            <td>Required only if ${auth_mechanism} is selected as api_key. Leave empty if 'instance_principal' or 'session_token' is used. Path of API Private Key (PEM Key) File </td>
            <td>Defaults to /cd3user/tenancies/keys/oci_api_private.pem when left empty</td>
        </tr>
        <tr>
            <td>fingerprint</td>
            <td>Required only if ${auth_mechanism} is selected as api_key. Leave empty if 'instance_principal' or 'session_token' is used</td>
            <td>9f:20:0b:....:8c</td>
        </tr>
        <tr>
            <td>outdir_structure_file</td>
            <td>The outdir_structure_file defines the grouping of the terraform auto.tf.vars for the various generated resources.To group resources into different directories within each region - specify the absolute path to the file.To have all the files generated in a single directory in the corresponding region, leave this variable blank.</td>
            <td>Defaults to /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/outdir_structure_file.properties</td>
        </tr>
        <tr>
            <td>ssh_public_key</td>
            <td>SSH Key for launched instances; Use '\n' as the delimiter to add multiple ssh keys.</td>
            <td>"ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"</td>
        </tr>
    </table>
</details>

<details>
    <summary> Advanced Parameters - Fill this to use toolkit with Jenkins </summary>
    <table style="width:100%">
        <tr>
            <th style="width:25%">Parameter</th>
            <th style="width:50%">Description</th>
            <th style="width:25%">Example</th>
        </tr>
        <tr>
            <td>compartment_ocid</td>
            <td>Compartment OCID where Bucket and DevOps Project/repo will be created; defaults to root if left empty.</td>
            <td>ocid1.compartment.oc1..aaaaaaaa7....ga</td>
        </tr>
        <tr>
            <td>use_remote_state</td>
            <td>Remote state configuration: Enter yes if remote state needs to be configured, else tfstate will be stored on local filesystem. Needs to be set as "yes" for Jenkins. </td>
            <td>yes/no</td>
        </tr>
        <tr>
            <td>remote_state_bucket_name</td>
            <td>Specify bucket name if you want to use existing bucket else leave empty.If left empty, Bucket with name ${customer_name}-automation-toolkit-bucket will be created/reused in ${region}.</td>
            <td>demo_bucket</td>
        </tr>
        <tr>
            <td>use_oci_devops_git</td>
            <td>OCI DevOps GIT configuration: Enter yes if generated terraform_files need to be stored in OCI DevOps GIT Repo else they will be stored on local filesystem. Will enforce 'yes' for use_remote_state in case this value is set to 'yes'. Needs to be set as "yes" for Jenkins. </td>
            <td>yes/no</td>
        </tr>
        <tr>
            <td>oci_devops_git_repo_name</td>
            <td>Specify Repo name if you want to use existing OCI Devops GIT Repository else leave empty Format: <project_name/repo_name\>. If left empty, DevOps items  with names <b>${customer_name}-automation-toolkit-project/repo/topic</b> will be created/reused in ${region}.</td>
            <td>demo_repo</td>
        </tr>
        <tr>
            <td>oci_devops_git_user</td>
            <td>User Details to perform GIT operations in OCI Devops GIT Repo. 
        Mandatory when using $(auth_mechanism) as instance_principal or session_token. 
        Format: <b>&lt;domainName&gt;/&lt;userName&gt;@&lt;tenancyName&gt;</b>
        When left empty, it will be fetched from $(user_ocid) for $(auth_mechanism) as api_key. 
        Customer Secret Key will also be configured for this user for S3 credentials of the bucket when $(auth_mechanism) is instance_principal or session_token</td>
            <td>oracleidentitycloudservice/devopsuser@oracle.com@ocitenant</td>
        </tr>
        <tr>
            <td>oci_devops_git_key</td>
            <td>When left empty, same key file from $(key_path) used for $(auth_mechanism) as api_key will be copied to <b>/cd3user/tenancies/&lt;customer_name&gt;/</b> and used for GIT Operations. Make sure the api key file permissions are rw(600) for cd3user</td>
            <td>/cd3user/tenancies/keys/oci_api_private.pem</td>
        </tr>
    </table>

</details>

!!! Important "Important"
    - Have the details ready for Authentication mechanism you are planning to use
    - Review **outdir_structure_file** parameter as per requirements. It is recommended to use separate outdir structure to manage a large number of resources
    - Review Advanced Parameters Section for CI/CD setup. Specifying these parameters as **'yes'** in properties file will create Object Storage Bucket and Devops Git Repo/Project/Topic in OCI and enable toolkit usage with Jenkins. The toolkit supports users in primary IDCS stripes or default domains only for DevOps GIT operations
    
- Initialise the environment to use the Automation Toolkit.
```
python createTenancyConfig.py tenancyconfig.properties
```

    !!! note 
        * Running the above command immediately after adding API key to the user profile in OCI might result in  Authentication Errors. In such cases, retry after a minute.



-  Example execution of the script with Advanced Parameters for CI/CD

    <img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="../images/connecttotenancy.png">

After the containers are successfully connected to the source and target OCI Tenancies, follow the steps below for cloning. 
## Initiate and Access Jenkins

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

* Access Jenkins URL using: ```https://<IP of the Jenkins Host>:<Port>``` 
  <br>
!!! note
      - ```<Port>``` is the port mapped with local system while docker container creation Eg: 8443.
      -  Network Connectivity should be allowed on this host and port.
      -  Please make sure to use a private server or a bastion connected server with restricted access(i.e. not publicly available).

  - It will prompt to create the first user to access Jenkins URL. This will be the admin user.
  - The Automation Toolkit only supports a single user Jenkins setup in this release.
  - After logging in, Jenkins Dashboard will be displayed.

## Step 1 : Export OCI **Network** and **Compute** Resources to an Excel sheet from Source OCI Tenancy

1. After logging in to Jenkins, click **Dashboard**, **setUpOCI pipeline** and **Build with Parameters**

2. Download the CD3 blank template from here:[CD3-Blank-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and upload it under the **Excel Template** section

3. Under **Workflow**, select **Export Existing Resources from OCI (Non-Greenfield Workflow; Import into excel and tfstate)**

4. Under **MainOptions**, select **Export Network and Export Compute**

5. Under **SubOptions**, select **Export all Network Components** for network and **Export Instances (excludes instances launched by OKE)** for compute

<img alt="Export_Resource" src="../images/Export_Resource.png" width="500" height="500">

## Step 2 : Create  OCI **Network** and **Compute** Resources to Target OCI Tenancy

1. Click **Dashboard**, **setUpOCI pipeline** and **Build with Parameters**

2. Under the **Excel Template** section, upload the updated Excel File from Step 1 above

3. Under **Workflow**, select **Create New Resources in OCI (Greenfield Workflow)**

4. Under **MainOptions**, select **Network** and **Compute**.

5. Under **SubOptions**, select **Create Network**, **Add/Modify/Delete Instances/Boot Backup Policy**

6. Click **Build**. The setUpOCI pipeline stages are executed in order

<img alt="Create_Resource" src="../images/Create_Resource.png" width="500" height="500">

Please Select appropriate **MainOptions** and **SubOptions** to export or create other OCI Resources.

This is how the CD3 automation toolkit enables ISVs or any individual users to achieve effortless, error-free cloning of OCI infrastructure across tenancies/compartments using Jenkin Pipelines. This approach ensures consistent infrastructure across your deployments.
