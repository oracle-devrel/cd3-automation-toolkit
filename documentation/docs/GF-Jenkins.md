# Provisioning of Instances/OKE/SDDC/Database on OCI via Jenkins

To provision OCI resources which require input ssh keys and source image details, update **variables_<region\>.tf** file using CLI.

**Step 1**: 
<br> Update required data in ```/cd3user/tenancies/<customer_name>/terraform_files/<region>/<service_dir>/variables_<region>.tf```

**Step 2**: 
<br>Execute GIT commands to sync these local changes with DevOps GIT Repo. Here are the [Steps](cli_jenkins.md)

**Step 3**: 
<br> Execute setUpOCI pipeline from Jenkins dashboard with workflow type as **Create Resources in OCI(Greenfield Workflow)** and choose the respective options to create required services.


