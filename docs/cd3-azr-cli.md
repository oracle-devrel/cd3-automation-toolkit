# **Set Up Azure using Automation Toolkit with CLI**
---
!!! Important "Must Read!"
    Check out the <a href="../must-read-prerequisites"><u>Must Read</u></a> section for managing network, compute and oci firewall resources.

## High Level Steps to use toolkit with CLI

1. Login to the CD3 Container.

2. Check out <a href="../cd3workflows"><u>CD3 Workflows document</u></a> for workflows supported by the toolkit and choose the workflow.

3. Use one of the templates from <a href="../excel-templates"><u>Excel Templates</u></a> based on the workflow chosen.

4. Review setUpAzure.properties file _/cd3user/azure/<prefix\>/<prefix\>_setUpAzure.properties_.

<span style="color: teal;"><b>setUpAzure.properties</b></span>
```ini
[Default]

#Input variables required to run setUpAzure script

#path to output directory where terraform file will be generated. eg /cd3user/azure/<prefix>/terraform_files
outdir=

#prefix for output terraform files eg demo
prefix=

# Auth Params
subscription_id=

tenant_id=

client_id=

client_secret=

#path to cd3 excel eg /cd3user/azure/<prefix>\CD3-Customer.xlsx
cd3file=

#specify create_resources to create new resources in Azure(greenfield workflow)
#specify export_resources to export resources from Azure(non-greenfield workflow)
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
            <td>/cd3user/azure/demo/terraform_files</td>
        </tr>
        <tr>
            <td>prefix</td>
            <td>Prefix for output terraform files</td>
            <td>demo</td>
        </tr>
        <tr>
            <td> subscription_id</td>
            <<td>azure subscription id</td>
            <td>155d83b2-....-....-....-ff5455dc5bdc</td>
        </tr>
        <tr>
            <td>tenant_id</td>
            <td>azure subscription tenant id</td>
            <td>89b6314d-....-....-....-0c37ec95f20e</td>
        </tr>
        <tr>
            <td>client_id</td>
            <td>service principal appid</td>
            <td>6950d59b-....-....-....-0039be18d7df</td>
        </tr>
        <tr>
            <td>client_secret</td>
            <td>service principal password</td>
            <td>.1..8Q~Xtch...........L5LxiPWb2vd_oaOP</td>
        </tr>
        <tr>
            <td>cd3file</td>
            <td>Path to the Excel input file</td>
            <td>/cd3user/azure/demo/CD3demo.xlsx</td>
        </tr>
        <tr>
            <td>workflow_type</td>
            <td>Create Resources in Azure or Export Resources from Azure</td>
            <td>create_resources or export_resources</td>
        </tr>
    </table>
</details>



## Copy CD3 Excel File

* While using the container launched using <a href="../launch-from-rmstack"><u>RM Stack</u></a>, local path `/cd3user/mount_path` on the VM is mapped to `/cd3user/tenancies` inside the container. So the Excel template can be copied at `/cd3user/mount_path/<prefix/>` on the VM. Below is the sample command to copy the Excel template from local system to container:
```
scp -i <private key pushed to VM while creating stack> <path to excel file on local> cd3user@<Public/Private IP of the VM>:/cd3user/mount_path/<prefix>
``` 

* Note that the user `cd3user` can be used to connect to the VM because same key is pushed for `opc` as well as `cd3user`.