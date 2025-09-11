# **Connect CD3 Container to Azure Subscription**
---

Connecting the CD3 container to an Azure Subscription authenticates the toolkit, allowing it to create, update, or export resources from the azure portal.

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
  


<span style="color: teal; font-weight: bold;">2 - Edit connectAzure.properties</span>

* Run 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/
  ```

* Fill the input parameters in ```connectAzure.properties ``` file. Expand below tables for parameter description and sample data. 
  Description for each parameter is also provided within the file.


📋 <b><i> connectAzure.properties </i></b>

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
            <td>Friendly name for the Azure Subscription</td>
            <td>demo</td>
            <td>Yes</td>

        </tr>
        <tr>
            <td>subscription_id</td>
            <td>azure subscription id</td>
            <td>155d83b2-....-....-....-ff5455dc5bdc</td>
            <td>No</td>

        </tr>
        <tr>
            <td>tenant_id</td>
            <td>azure subscription tenant id</td>
            <td>89b6314d-....-....-....-0c37ec95f20e</td>
            <td>No</td>
        </tr>
        <tr>
            <td>client_id</td>
            <td>service principal appid</td>
            <td>6950d59b-....-....-....-0039be18d7df</td>
            <td>No</td>
        </tr>
        <tr>
            <td>client_secret</td>
            <td>service principal password</td>
            <td>.1..8Q~Xtch...........L5LxiPWb2vd_oaOP</td>
            <td>No</td>
        </tr>
        
    </table>

</details>

<br>

!!! tip " Important Configuration Tips"
    - Auth Details Parameters are optional.<br>
    - If left empty, the toolkit will not be able to run any APIs against the Azure subscription. <br>
    - This will mean that - <br>
       Toolkit will be able to generate just the terraform (tfvars files) without having the ability to apply it. Also export workflow will not be executed.
    

 

<span style="color: teal; font-weight: bold;">4 - Initialise the environment</span>

* Initialise your environment to use the Automation Toolkit with Azure Cloud.
```
python connectCloud.py azure connectAzure.properties
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
            <td>setUpAzure.properties</td>
            <td>/cd3user/azure/&lt;prefix&gt;/&lt;prefix>_setUpAzure.properties</td>
            <td>Subscription Specific properties file</td>
        </tr>
        
        <tr>
            <td>Terraform files directory</td>
            <td>/cd3user/azure/&lt;prefix&gt;/terraform_files</td>
            <td>outdir for the generation of terraform files.</td>
        </tr>
        <tr>
            <td>Variables File,Provider File, Root and Sub terraform modules</td>
            <td>/cd3user/azure/&lt;prefix&gt;/terraform_files/</td>
            <td>Required for terraform to work. Variables file and Provider file will contain authentication parameters if provided while running above script.</td>
        </tr>
        <tr>
            <td>out file</td>
            <td>/cd3user/azure/&lt;prefix&gt;/.config_files/connectAzure.out</td>
            <td>This file contains a copy of information displayed as the console output of the script</td>
        </tr>
        <tr>
            <td>connectAzure.properties</td>
            <td>/cd3user/azure/&lt;prefix&gt;/.config_files/&lt;prefix&gt;_connectAzure.properties</td>
            <td>The input properties file used to execute the script is copied to prefix folder to retain for future reference. This can be used when the script needs to be re-run with same parameters at later stage.</td>
        </tr>        
    </table>
</details>

<details>
    <summary> Example execution of the script </summary>

    <img width="1124" alt="Screenshot 2024-01-10 at 5 54 02 PM" src="../images/connecttotenancy.png">

</details>

<br>


!!! info "Managing Multiple Prefixes?" 
    Need to manage multiple environments separately by using distinct prefixes, all within a single CD3 container?<br>
    Check this out: [Multiple Prefixes](multiple-prefixes.md)


Proceed to the below instructions:

[Set Up Azure using Automation Toolkit](setUpAzure.md){ .md-button }