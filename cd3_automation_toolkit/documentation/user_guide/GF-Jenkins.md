# Provisioning of Instances/OKE/SDDC/Database on OCI via Jenkins

To provision OCI resources which require input ssh keys and source image details, update variables_\<region\>.tf file using CLI.

**Step 1**: 
<br> Update required data in `/cd3user/tenancies/<customer_name>/terraform_files/<region>/<service_dir>/variables_<region>.tf`

**Step 2**: 
<br>Execute GIT commands to synch these local changes with DevOps GIT Repo. Here are the <a href = "/cd3_automation_toolkit/documentation/user_guide/cli_jenkins.md">steps.</a>

**Step 3**: 
<br> Execute setUpOCI pipeline from Jenkins dashboard with workflow type as 'Create Resources in OCI(Greenfield Workflow)' and chose the respective options to create required services.


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField-Jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
