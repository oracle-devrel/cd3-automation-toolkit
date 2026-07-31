# **Manage GCP using Automation Toolkit with CLI**
---
## High Level Steps to use toolkit with CLI

1. Login to the CD3 Container.

2. Check out <a href="../cd3workflows"><u>CD3 Workflows document</u></a> for workflows supported by the toolkit and choose the required workflow.

3. Use GCP excel template from <a href="../excel-templates"><u>Excel Templates</u></a> based on your requirement.

4. Review `setUpGCP.properties` file:  `/cd3user/gcp/<prefix>/<prefix>_setUpGCP.properties`.

<span style="color: teal;"><b>setUpGCP.properties</b></span>
```ini
[Default]

#Input variables required to run setUpGCP script

#path to output directory where terraform file will be generated. eg /cd3user/gcp/<prefix>/terraform_files
outdir=

#prefix for output terraform files eg demo
prefix=

# Auth Params
auth_mechanism=

#input credentials file for service account eg /cd3user/gcp/<prefix>/gcp_api_private.json
config_file=

#path to cd3 excel eg /cd3user/gcp/<prefix>\CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in GCP(greenfield workflow)
#specify export_resources to export resources from GCP(non-greenfield workflow)
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
            <td>/cd3user/gcp/demo/terraform_files</td>
        </tr>
        <tr>
            <td>prefix</td>
            <td>Prefix for output terraform files</td>
            <td>demo</td>
        </tr>
        <tr>
            <td>auth_mechanism</td>
            <<td> api_key of service account </td>
            <td>api_key</td>
        </tr>
        <tr>
            <td>config_file</td>
            <td>input credentials file for service account</td>
            <td>/cd3user/gcp/keys/gcp_api_private.json</td>
        </tr>
        <tr>
            <td>cd3file</td>
            <td>Path to the Excel input file</td>
            <td>/cd3user/gcp/demo/CD3demo.xlsx</td>
        </tr>
        <tr>
            <td>workflow_type</td>
            <td>Create Resources in GCP or Export Resources from GCP</td>
            <td>create_resources or export_resources</td>
        </tr>
    </table>
</details>



## Copy CD3 Excel File

* While using the container launched using <a href="../launch-from-rmstack"><u>RM Stack</u></a>, local path `/cd3user/mount_path` on the VM is mapped to `/cd3user/` inside the container. So the Excel template can be copied at `/cd3user/mount_path/gcp/<prefix>/` on the VM. Below is the sample command to copy the Excel template from local system to container:
```
scp -i <private key pushed to VM while creating stack> <path to excel file on local> cd3user@<Public/Private IP of the VM>:/cd3user/mount_path/gcp/<prefix>
``` 

* Note that the user `cd3user` can be used to connect to the VM because same key is pushed for `opc` as well as `cd3user`.