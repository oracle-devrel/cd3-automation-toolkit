# **Using the Automation Toolkit with CLI**
---
!!! Important
    Make sure to read 'Must Read' sections before creating or exporting network and compute resources.

Below are the highlevel steps to generate terraform with CLI - <br>

1. Login to the CD3 Container.

2. Check out [Launch CD3 Container](launch-container.md) for workflows supported by the toolkit and choose the workflow.

3. Use one of the templates from [Excel Templates](excel-templates.md) based on the workflow chosen.

4. Review setUpOCI.properties file _/cd3user/tenancies/<customer_name\>/<customer_name\>_setUpOCI.properties_.

_setUpOCI.properties_
```ini
[Default]

#Input variables required to run setUpOCI script

#path to output directory where terraform file will be generated. eg /cd3user/tenancies/<customer_name>/terraform_files
outdir=

#prefix for output terraform files eg <customer_name> like demotenancy
prefix=

# auth mechanism for OCI APIs - api_key,instance_principal,session_token
auth_mechanism=

#input config file for Python API communication with OCI eg /cd3user/tenancies/<customer_name>/.config_files/<customer_name>_config;
config_file=

# Leave it blank if you want single outdir or specify outdir_structure_file.properties containing directory structure for OCI services.
outdir_structure_file=

#path to cd3 excel eg /cd3user/tenancies/<customer_name>\CD3-Customer.xlsx
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
            <td>/cd3user/tenancies//terraform_files</td>
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
            <td>/cd3user/tenancies//.config_files/_config</td>
        </tr>
        <tr>
            <td>outdir_structure_file</td>
            <td>Parameter specifying single outdir or different for different services</td>
            <td>Blank or _outdir_structure_file.properties</td>
        </tr>
        <tr>
            <td>cd3file</td>
            <td>Path to the Excel input file</td>
            <td>/cd3user/tenancies//testCD3. xlsx</td>
        </tr>
        <tr>
            <td>workflow_type</td>
            <td>Create Resources in OCI or Export Resources from OCI</td>
            <td>create_resources or export_resources</td>
        </tr>
    </table>
</details>