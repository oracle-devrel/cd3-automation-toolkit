# Updating variables_\<region\>.tf file for provisioning Instances/OKE/SDDC/Database on OCI

Provisioning of OCI resources like - Compute instances, SDDC, OKE and Databases require you to update variables_\<region\>.tf file with input ssh keys and source image details.
This file needs to be updated with required details(like input SSH keys or source image details) via CLI when you are using the toolkit via Jenkins.

**Step 1**: 
<br> Update required data in variables_<region>.tf

**Step 2**: 
<br>Please follow steps described <a href = "/cd3_automation_toolkit/documentation/user_guide/cli_jenkins.md">here</a> to synch these local changes with DevOps GIT Repo

**Step 3**: 
<br> Execute setUpOCI pipeline from Jenkins dashboard with workflow type as 'Create Resources in OCI(Greenfield Workflow)' and chose the respective options to create required services.


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField-Jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
