# **Using the Automation Toolkit with CLI**
---
!!! Important
    Check out the <a href="../must-read-prerequisites"><u>Must Read</u></a> section for managing network, compute and oci firewall resources.

## **High Level Steps to use toolkit with CLI**

1. Login to the CD3 Container.

2. Check out <a href="../cd3-overview#cd3-toolkit-process"><u>CD3 Toolkit Process</u></a> for workflows supported by the toolkit and choose the workflow.

3. Use one of the templates from <a href="../excel-templates"><u>Excel Templates</u></a> based on the workflow chosen.

4. Review setUpOCI.properties file _/cd3user/tenancies/<prefix\>/<prefix\>_setUpOCI.properties_.

_setUpOCI.properties_
```ini
[Default]

#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<prefix>/terraform_files
outdir=

#prefix for output terraform files eg <customer_name> like demotenancy
prefix=

# auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=

#input config file for Python API communication with OCI eg /cd3user/tenancies/<prefix>/.config_files/<prefix>_config;
config_file=

# Leave it blank if you want single outdir or specify outdir_structure_file.properties containing directory structure for OCI services.
outdir_structure_file=

# IaC Tool to be configured - Terraform(specify terraform) or OpenTofu(specify tofu)
tf_or_tofu=tofu

#path to cd3 excel eg /cd3user/tenancies/<prefix>\CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in OCI(greenfield workflow)
#specify export_resources to export resources from OCI(non-greenfield workflow)
workflow_type=create_resources
```


<details>
    <summary> Parameter Description </summary>
    <table>
        <tr>
            <th>Variable</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>outdir</td>
            <td>Path to output directory where terraform files will be generated</td>
            <td>/cd3user/tenancies/demo/terraform_files</td>
        </tr>
        <tr>
            <td>prefix</td>
            <td>Prefix for output terraform files</td>
            <td>\</td>
        </tr>
        <tr>
            <td>auth_mechanism</td>
            <td>Authentication Mechanism for OCI APIs</td>
            <td>api_key</td>
        </tr>
        <tr>
            <td>config_file</td>
            <td>Python config file	</td>
            <td>/cd3user/tenancies/demo/.config_files/_config</td>
        </tr>
        <tr>
            <td>outdir_structure_file</td>
            <td>Parameter specifying single outdir or different for different services</td>
            <td>Blank or _outdir_structure_file.properties</td>
        </tr>
        <tr>
            <td>tf_or_tofu</td>
            <td>IaC Tool to be configured - Terraform or OpenTofu</td>
            <td>terraform or tofu</td>
        </tr>
        <tr>
            <td>cd3file</td>
            <td>Path to the Excel input file</td>
            <td>/cd3user/tenancies/demo/CD3demo.xlsx</td>
        </tr>
        <tr>
            <td>workflow_type</td>
            <td>Create Resources in OCI or Export Resources from OCI</td>
            <td>create_resources or export_resources</td>
        </tr>
    </table>
</details>

## **Copy CD3 Excel File**
* While using the container launched using <a href="../launch-from-rmstack"><u>RM Stack</u></a>, local path _/cd3user/mount_path_ on the VM is mapped to _/cd3user/tenancies_ inside the container. So the file can be copied at _/cd3user/mount_path/<prefix\>_ on the VM. Below is the sample command to copy the excel file from local system to container:
```
scp -i <private key pushed to VM while creating stack> <path to excel file on local> cd3user@<Public/Private IP of the VM>:/cd3user/mount_path/<prefix>
``` 
Note that cd3user can be used to connect to the VM because same key is pushed for opc as well as cd3user.