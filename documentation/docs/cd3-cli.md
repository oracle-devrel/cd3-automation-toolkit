# **Using the Automation Toolkit with CLI**
---

To start generating terraform using the toolkit with CLI, make sure below things are ready:<br>

1. Login to the CD3 Container.

2. [Read](cd3-overview.md) for workflows supported by the toolkit and chose the workflow.

3. Use one of the templates at [Excel Templates](excel-templates.md) based on the workflow chosen.

4. Review setUpOCI.properties file _/cd3user/tenancies/<customer_name\>/<customer_name\>_setUpOCI.properties_.

_Current Version: v2024.1.0_
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

| Variable | Description | Example |
|---|---|---|
|outdir|Path to output directory where terraform files will be generated| /cd3user/tenancies/<customer\_name>/terraform\_files|
|prefix|Prefix for output terraform files|\<customer\_name>|
|auth_mechanism|Authentication Mechanism for OCI APIs|api_key|
|config\_file|Python config file|/cd3user/tenancies/<customer\_name>/.config_files/<customer\_name>_config|
|outdir\_structure\_file |Parameter specifying single outdir or different for different services|Blank or <customer\_name>_outdir_structure_file.properties|
| cd3file |Path to the Excel input file |/cd3user/tenancies/<customer\_name>/testCD3. xlsx |
|workflow\_type |Create Resources in OCI or Export Resources from OCI | create_resources or export_resources |

