# Restructuring Terraform Out Directory (Creating independent tfstate files for each resource)
CD3 Automation Toolkit used to generate all the output terraform files in a single region directory earlier.
OCI components like - network, instances, LBaaS, Databases etc were maintained in a single tfstate file.
This was not a viable option for tenancies requiring huge infrastructure.

With Automation Toolkit release v10.1, it allows you to choose different directories for each OCI service supported by toolkit.
This can be configured while [connecting your container to the OCI tenancy](/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md#connect-docker-container-to-oci-tenancy)
A new parameter 'outdir_structure_file' has been introduced in tenancyconfig.properties using which you can use to configure single outdir or different outdir for each service.

  <br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosNGF.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/KnownBehaviour.md">Next :arrow_forward:</a> |
| :---- | -------: |

