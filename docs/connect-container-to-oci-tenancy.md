# **Connect CD3 Container to OCI Tenancy**
---

Connecting the CD3 container to an OCI tenancy authenticates the toolkit, allowing it to create, update, or export resources from the tenancy.

<br>

**🛠️  Steps:**


<span style="color: teal; font-weight: bold;">1 - Login (Exec) into the Container</span>

* Login to the previously launched container using either <a href ="../launch-from-rmstack"><u>RM Stack</u></a> or <a href ="../launch-from-local"><u>Manual Launch</u></a>.

    === "RM Stack(Podman)"
        ```
        sudo podman exec -it cd3_toolkit bash
        ```

    === "Manual Launch(Docker) "
        ```
        sudo docker exec -it cd3_toolkit bash
        ```
  


<span style="color: teal; font-weight: bold;">2 - Choose Authentication Mechanism for OCI SDK</span>

* <a href ="../authmechanisms"><u>Click here</u></a> to configure any one of the available authentication mechanisms.

!!! Warning "Access Requirements"
  
    Make sure to assign required OCI Tenancy Access to user/instance as defined in <a href ="../prerequisites"><u>Prerequisites.</u></a>

  

<span style="color: teal; font-weight: bold;">3 - Edit tenancyconfig.properties</span>

* Run 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/
  ```

* Fill the input parameters in ```tenancyconfig.properties``` file. Expand below tables for parameter description and sample data. 
  Description for each parameter is also provided within the file.


📋 <b><i>tenancyconfig.properties</i></b>

<details>
    <summary> Parameter Description </summary>
    <table>
        <tr>
            <th>Parameter</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>prefix</td>
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
            <td>tf_or_tofu</td>
            <td>IaC Tool to be configured - Terraform or OpenTofu</td>
            <td>terraform</td>
        </tr>
        <tr>
        <tr>
            <td>ssh_public_key</td>
            <td>SSH Key for launched instances; Use '\n' as the delimiter to add multiple ssh keys.</td>
            <td>ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf</td>
        </tr>
    </table>
</details>



<details>
    <summary> Advanced Parameters - To use toolkit with Jenkins </summary>
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
            <td>Specify bucket name if you want to use existing bucket else leave empty.If left empty, Bucket with name ${prefix}-automation-toolkit-bucket will be created/reused in ${region}.</td>
            <td>demo_bucket</td>
        </tr>
        <tr>
            <td>use_oci_devops_git</td>
            <td>OCI DevOps GIT configuration: Enter yes if generated terraform_files need to be stored in OCI DevOps GIT Repo else they will be stored on local filesystem. Will enforce 'yes' for use_remote_state in case this value is set to 'yes'. Needs to be set as "yes" for Jenkins. </td>
            <td>yes/no</td>
        </tr>
        <tr>
            <td>oci_devops_git_repo_name</td>
            <td>Specify Repo name if you want to use existing OCI Devops GIT Repository else leave empty Format: <project_name/repo_name\>. If left empty, DevOps items  with names <b>${prefix}-automation-toolkit-project/repo/topic</b> will be created/reused in ${region}.</td>
            <td>demo_repo</td>
        </tr>
        <tr>
            <td>oci_devops_git_user</td>
            <td>User Details to perform GIT operations in OCI Devops GIT Repo. 
        Mandatory when using $(auth_mechanism) as instance_principal or session_token. 
        Format: <b>&lt;domainName&gt;/&lt;userName&gt;@&lt;tenancyName&gt;</b>
        When left empty, it will be fetched from $(user_ocid) for $(auth_mechanism) as api_key. 
        Customer Secret Key will also be configured for this user for S3 credentials of the bucket when $(auth_mechanism) is instance_principal or session_token

	<b>Users in Custom Domain are not supported as of now.</td>
            <td>oracleidentitycloudservice/devopsuser@oracle.com@ocitenant</td>
        </tr>
        <tr>
            <td>oci_devops_git_key</td>
            <td>When left empty, same key file from $(key_path) used for $(auth_mechanism) as api_key will be copied to <b>/cd3user/tenancies/&lt;prefix&gt;/</b> and used for GIT Operations. Make sure the api key file permissions are rw(600) for cd3user</td>
            <td>/cd3user/tenancies/keys/oci_api_private.pem</td>
        </tr>
    </table>

</details>

<br>

!!! tip " Important Configuration Tips"
    - Have the details ready for Authentication mechanism you are planning to use.<br>
    - Choose whether the outdir needs to be configured with OpenTofu or Terraform. Its a one time selection for that prefix and cannot be modified later.<br>
    - Review **outdir_structure_file** parameter as per requirements. It is recommended to use separate outdir structure to manage a large number of resources. <br>
    - Review Advanced Parameters Section for CI/CD setup. **The toolkit can be used either with CLI or with Jenkins.** If you plan to use the toolkit with Jenkins then be ready with user details that will be used to connect to DevOps Repo in OCI. Specifying these parameters as **'yes'** in properties file will create Object Storage Bucket and Devops Git Repo/Project/Topic in OCI and enable toolkit usage with Jenkins. The toolkit supports users in primary IDCS stripes or default domains only for DevOps GIT operations.<br>

 

<span style="color: teal; font-weight: bold;">4 - Initialise the environment</span>

* Initialise your environment to use the Automation Toolkit.
```
python createTenancyConfig.py tenancyconfig.properties
```

    !!! warning "Heads-Up!"
        * When running the CD3 container on a Linux VM host (without using the Resource Manager stack option), refer to <a href="../faq"><u>point no. 7</u></a> under FAQ to avoid any permission issues.
        * Running the above command immediately after adding API key to the user profile in OCI might result in  Authentication Errors. In such cases, retry after a minute.




**Output:**

<details>
    <summary> Output files and OCI resources - </summary>
    <table>
        <tr>
            <th>Files Generated</th>
            <th>At File Path</th>
            <th>Comment/Purpose</th>
        </tr>
        <tr>
            <td>setUpOCI.properties</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/&lt;prefix>_setUpOCI.properties</td>
            <td>Customer Specific properties</td>
        </tr>
        <tr>
            <td>outdir_structure_file.properties</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/&lt;prefix&gt;_outdir_structure_file</td>
            <td>Customer Specific properties file for outdir structure.
            This file will not be generated if 'outdir_structure_file' parameter was set to empty(single outdir)in tenancyconfig.properties while running createTenancyConfig.py</td>
        </tr>
        <tr>
            <td>Region based directories</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/terraform_files</td>
            <td>Tenancy's subscribed regions based directories for the generation of terraform files.
                Each region directory will contain individual directory for each service based on the parameter 'outdir_structure_file'</td>
        </tr>
        <tr>
            <td>Variables File,Provider File, Root and Sub terraform modules</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/terraform_files/&lt;region></td>
            <td>Required for terraform to work. Variables file and Provider file will be generated based on authentication mechanism chosen.</td>
        </tr>
        <tr>
            <td>out file</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/createTenancyConfig.out</td>
            <td>This file contains a copy of information displayed as the console output.</td>
        </tr>
        <tr>
            <td>OCI Config File</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/.config_files/&lt;prefix&gt;_oci_config</td>
            <td>Customer specific Config file for OCI API calls. This will have data based on authentication mechanism chosen.</td>
        </tr>
        <tr>
            <td>Public and Private Key Pair</td>
            <td>Copied from /cd3user/tenancies/keys/ to /cd3user/tenancies/&lt;prefix&gt;/.config_files</td>
            <td>API Key for authentication mechanism as API_Key are copied to customer specific out directory locations for easy access.</td>
        </tr>
        <tr>
            <td>GIT Config File</td>
            <td>/cd3user/tenancies/jenkins_home/git_config</td>
            <td>GIT Config file for OCI Dev Ops GIT operations.This is generated only if use_oci_devops_git is set to yes. Symlink is created for this file at /cd3user/.ssh/config</td>
        </tr>
        <tr>
            <td>S3 Credentials File</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/.config_files/&lt;prefix&gt;_s3_credentials</td>
            <td>This file contains access key and secret for S3 compatible bucket to manage remote terraform state. This is generated only if use_remote_state is set to yes</td>
        </tr>
        <tr>
            <td>Jenkins Home</td>
            <td>/cd3user/tenancies/jenkins_home</td>
            <td>This folder contains jenkins specific data. Single Jenkins instance can be setup for a single container.</td>
        </tr>
        <tr>
            <td>tenancyconfig.properties</td>
            <td>/cd3user/tenancies/&lt;prefix&gt;/.config_files/&lt;prefix&gt;_tenancyconfig.properties</td>
            <td>The input properties file used to execute the script is copied to customer folder to retain for future reference. This can be used when the script needs to be re-run with same parameters at later stage.</td>
        </tr>
       <tr>
            <th>OCI Resources Created</th>
            <th>Name</th>
            <th>Comment/Purpose</th>
        </tr>

        <tr>
            <td>OCI DevOps Project and Repository</td>
            <td>&lt;prefix&gt;-automation-toolkit-project and &lt;prefix&gt;-automation-toolkit-repo</td>
            <td>Devops Project and repo are created under compartment specified under compartment_ocid property in tenancyconfig.properties. This will host the terraform/tofu code. This is created only if use_oci_devops_git is set to yes.</td>
        </tr>
        <tr>
            <td>OCI Topic</td>
            <td>&lt;prefix&gt;-automation-toolkit-topic </td>
            <td>An empty OCI Topic (without any subscription) is created which is needed for Devops Project.</td>
        </tr>
        <tr>
            <td>OCI Bucket</td>
            <td>&lt;prefix&gt;-automation-toolkit-bucket </td>
            <td>An OCI bucket is created to store the state file. This is created only if use_remote_state is set to yes.</td>
        </tr>
        <tr>
            <td>Customer Secret Key</td>
            <td>&lt;prefix&gt;-automation-toolkit-csk </td>
            <td>A Customer Secret Key is created for the user specified in tenancyconfig.properties file. This is used as S3 credentials for the bucket storing remote state.</td>
        </tr>
        
    </table>

</details>

<details>
    <summary> Example execution of the script with Advanced Parameters for CI/CD </summary>

    <img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="../images/connecttotenancy.png">

</details>

<br>

!!! abstract "Subscribing to a new OCI Region?"

    When a new region is subscribed to the tenancy, rerun `createTenancyConfig.py` by using the same `tenancyconfig.properties` file that was originally used.<br>
    ✅ It will create new directory for the new region under `/cd3user/tenancies/<prefix>/terraform_files` without modifying the existing ones <br>
    ✅ It will also commit the latest terraform_files folder to OCI DevOps GIT repo.


!!! info "Managing Multiple Prefixes?" 
    Need to manage multiple environments separately by using distinct prefixes, all within a single CD3 container?<br>
    Check this out: [Multiple Prefixes](multiple-prefixes.md)

<br>

Choose how to use the toolkit and follow the corresponding instructions:

[Use Toolkit with CLI](cd3-cli.md){ .md-button }    [Use Toolkit with Jenkins](cd3-jenkins.md){ .md-button }