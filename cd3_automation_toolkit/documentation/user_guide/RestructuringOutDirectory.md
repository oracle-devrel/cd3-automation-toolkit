# Restructuring Terraform Out Directory
CD3 Automation Toolkit used to generate all the output terraform files in a single region directory earlier.
OCI components like - network, instances, LBaaS, Databases etc were maintained in a single tfstate file.
This was not a viable option for tenancies requiring huge infrastructure.

With Automation Toolkit release v10.1, it allows you to choose different directories for each OCI service supported by toolkit.
This can be configured while connecting your container to the OCI tenancy.



