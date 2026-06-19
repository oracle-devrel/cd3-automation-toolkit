# **Connect CD3 Container to AWS account**
---

Connecting the CD3 container to an AWS account authenticates the toolkit, allowing it to create, update, or export resources from AWS Cloud.

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
  


<span style="color: teal; font-weight: bold;">2 - Edit connectAWS.properties</span>

* Run 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/
  ```

* Fill the input parameters in ```connectAWS.properties ``` file. Expand below tables for parameter description and sample data. 
  Description for each parameter is also provided within the file.


📋 <b><i> connectAWS.properties </i></b>

<details>
    <summary> Parameter Description </summary>
    <table>
        <tr>
            <th>Parameter</th>
            <th>Description</th>
            <th>Example</th>
	    <th>Mandatory<br>Parameter?</th>
        </tr>
        <tr>
            <td>prefix</td>
            <td>Friendly name for the AWS account environment</td>
            <td>demo</td>
            <td>Yes</td>
        </tr>
        <tr>
            <td>aws_access_key_id</td>
            <td>AWS Access Key</td>
            <td>AKIAIOSFODNN7EXAMPLE</td>
            <td>No</td>
        </tr>
        <tr>
            <td>aws_secret_access_key</td>
            <td>AWS Secret Key</td>
            <td>wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</td>
            <td>No</td>
        </tr>        
    </table>

</details>

<br>

!!! tip " Important Configuration Tips- Offline tfvars Generation"
    - Auth Details Parameters are optional.<br>
    - If left empty, the toolkit will not be able to run any APIs against the AWS account. <br>
    - This will mean that - <br>
       Toolkit will be able to generate just the terraform (tfvars files) without having the ability to apply it. Also export workflow will not be executed.
    

 

<span style="color: teal; font-weight: bold;">4 - Initialise the environment</span>

* Initialise your environment to use the Automation Toolkit with AWS account.
```
python connectCloud.py aws connectAWS.properties
```

    !!! warning "Heads-Up!"
        * When running the CD3 container on a Linux VM host (without using the Resource Manager stack option), refer to <a href="../faq"><u>point no. 7</u></a> under FAQ to avoid any permission issues.



**Output:**

<details>
    <summary> Output files </summary>
    <table>
        <tr>
            <th>Files Generated</th>
            <th>At File Path</th>
            <th>Comment/Purpose</th>
        </tr>
        <tr>
            <td>setUpAWS.properties</td>
            <td>/cd3user/aws/&lt;prefix&gt;/&lt;prefix>_setUpAWS.properties</td>
            <td>Account Specific properties file</td>
        </tr>
        
        <tr>
            <td>Terraform files directory</td>
            <td>/cd3user/aws/&lt;prefix&gt;/terraform_files</td>
            <td>outdir for the generation of terraform files.</td>
        </tr>
        <tr>
            <td>Variables File,Provider File, Root and Sub terraform modules</td>
            <td>/cd3user/aws/&lt;prefix&gt;/terraform_files/</td>
            <td>Required for terraform to work. Variables file and Provider file will contain authentication parameters if provided while running above script.</td>
        </tr>
        <tr>
            <td>out file</td>
            <td>/cd3user/aws/&lt;prefix&gt;/connectAWS.out</td>
            <td>This file contains a copy of information displayed as the console output of the script</td>
        </tr>
        <tr>
            <td>connectAWS.properties</td>
            <td>/cd3user/aws/&lt;prefix&gt;/.config_files/&lt;prefix&gt;_connectAWS.properties</td>
            <td>The input properties file used to execute the script is copied to prefix folder to retain for future reference. This can be used when the script needs to be re-run with same parameters at later stage.</td>
        </tr>        
    </table>
</details>

<details>
    <summary> Example execution of the script </summary>

    <img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="../images/connecttoaws.png">

</details>

<br>


!!! info "Managing Multiple Prefixes?" 
    Easily manage multiple environments in a single CD3 container using distinct prefixes.<br>
    Check this out: [Multiple Prefixes](multiple-prefixes.md)


After successful initialization, proceed to the below instructions:

[Manage AWS using Automation Toolkit](setUpAWS.md){ .md-button }