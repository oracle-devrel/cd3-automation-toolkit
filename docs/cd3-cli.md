# **Using the Automation Toolkit with CLI**
---

To start generating terraform using the toolkit with CLI, make sure below things are ready:<br>

1. Login to the CD3 Container.

2. [Read](launch-container.md) for workflows supported by the toolkit and chose the workflow.

3. Use one of the templates at [Excel Templates](excel-templates.md) based on the workflow chosen.

4. Review setUpOCI.properties file _/cd3user/tenancies/<customer_name\>/<customer_name\>_setUpOCI.properties_.

_Current Version: v2024.2.0_
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
    <summary> Details of the files created on successful execution of above steps </summary>
    <table>
        <tr>
            <th>Variable</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <th>outdir</th>
            <th>Path to output directory where terraform files will be generated</th>
            <th>/cd3user/tenancies//terraform_files</th>
        </tr>
        <tr>
            <th>prefix</th>
            <th>Prefix for output terraform files</th>
            <th>\</th>
        </tr>
        <tr>
            <th>auth_mechanism</th>
            <th>Authentication Mechanism for OCI APIs</th>
            <th>api_key</th>
        </tr>
        <tr>
            <th>config_file</th>
            <th>Python config file	</th>
            <th>/cd3user/tenancies//.config_files/_config</th>
        </tr>
        <tr>
            <th>outdir_structure_file</th>
            <th>Parameter specifying single outdir or different for different services</th>
            <th>Blank or _outdir_structure_file.properties</th>
        </tr>
        <tr>
            <th>cd3file</th>
            <th>Path to the Excel input file</th>
            <th>/cd3user/tenancies//testCD3. xlsx</th>
        </tr>
        <tr>
            <th>workflow_type</th>
            <th>Create Resources in OCI or Export Resources from OCI</th>
            <th>create_resources or export_resources</th>
        </tr>
    </table>
</details>