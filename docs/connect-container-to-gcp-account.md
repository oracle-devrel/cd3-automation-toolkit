# **Connect CD3 Container to GCP Account**
---

Connecting the CD3 container to an GCP Account authenticates the toolkit, allowing it to create, update, or export resources from GCP Cloud.

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
  


<span style="color: teal; font-weight: bold;">2 - Edit connectGCP.properties</span>

* Run 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/
  ```

* Fill the input parameters in ```connectGCP.properties ``` file. Expand below tables for parameter description and sample data. 
  Description for each parameter is also provided within the file.


📋 <b><i> connectGCP.properties </i></b>

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
            <td>Friendly name for the GCP Account. The generated .auto.tfvars files will be prefixed with this.</td>
            <td>demo</td>
            <td>Yes</td>

        </tr>
        <tr>
            <td>auth_mechanism</td>
            <td>Auth Mechanism for GCP APIs</td>
            <td>api_key</td>
            <td>No</td>

        </tr>
        <tr>
            <td>config_file</td>
            <td>Path to JSON file having private key information for the service account</td>
            <td>/cd3user/gcp/keys/gcp_api_private.json</td>
            <td>No</td>
        </tr>
        
    </table>

</details>

<br>

!!! tip " Important Configuration Tips- Offline tfvars Generation"
    - Auth Details Parameters are optional.<br>
    - If left empty, the toolkit will not be able to run any APIs against the GCP account. <br>
    - This will mean that - <br>
       Toolkit will be able to generate just the terraform (tfvars files) without having the ability to apply it. Also export workflow will not be executed.
    

 

<span style="color: teal; font-weight: bold;">4 - Initialise the environment</span>

* Initialise your environment to use the Automation Toolkit with GCP Cloud.
```
python connectCloud.py gcp connectGCP.properties
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
            <td>setUpGCP.properties</td>
            <td>/cd3user/gcp/&lt;prefix&gt;/&lt;prefix>_setUpGCP.properties</td>
            <td>Subscription Specific properties file</td>
        </tr>
        
        <tr>
            <td>Terraform files directory</td>
            <td>/cd3user/gcp/&lt;prefix&gt;/terraform_files</td>
            <td>outdir for the generation of terraform files.</td>
        </tr>
        <tr>
            <td>Variables File,Provider File, Root and Sub terraform modules</td>
            <td>/cd3user/gcp/&lt;prefix&gt;/terraform_files/</td>
            <td>Required for terraform to work. Variables file and Provider file will contain authentication parameters if provided while running above script.</td>
        </tr>
        <tr>
            <td>out file</td>
            <td>/cd3user/gcp/&lt;prefix&gt;/connectGCP.out</td>
            <td>This file contains a copy of information displayed as the console output of the script</td>
        </tr>
        <tr>
            <td>connectGCP.properties</td>
            <td>/cd3user/gcp/&lt;prefix&gt;/.config_files/&lt;prefix&gt;_connectGCP.properties</td>
            <td>The input properties file used to execute the script is copied to prefix folder to retain for future reference. This can be used when the script needs to be re-run with same parameters at later stage.</td>
        </tr>        
    </table>
</details>

<details>
    <summary> Example execution of the script </summary>

    <img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="../images/connecttogcp.png">

</details>

<br>


!!! info "Managing Multiple Prefixes?" 
    Easily manage multiple environments in a single CD3 container using distinct prefixes.<br>
    Check this out: [Multiple Prefixes](multiple-prefixes.md)


Proceed to the below instructions:

[Manage GCP using Automation Toolkit](setUpGCP.md){ .md-button }