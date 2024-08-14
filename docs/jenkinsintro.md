# Jenkins Dashboard

!!! Important
    Check out the [Must Read](must-read-prerequisites.md) section for managing network, compute and oci firewall resources.

<br>

<img width="1486" alt="Jenkins-Arch" src="../images/jenkinsoverview-0.png">

<br>
   
<img width="1486" alt="Jenkins-Dashboard" src="../images/jenkinsoverview-1.jpg">

<b>

1. setupoci Pipeline

2. terraform_files Folder

3. Region based Views (including Global directory)

</b>

### <b>1. setupoci Pipeline</b>

This is equivalent to running *setupoci.py* from CLI. This will generate the **.auto.tfvars** files based on the CD3 Excel sheet input for the services chosen and commit them to OCI Devops GIT repo. Additionally, it also triggers **apply** pipelines for the corresponding services chosen in setupoci pipeline.

Below table shows the stages executed in this pipeline along with their description:


<b><i>setupoci Pipeline Stages</i></b>

|Stage Name      | Description  | Possible Outcomes |
| --------------- | ------------ | ----------------- |
| <b>Validate Input Parameters</b> | Validates input file name/size, selected parameters | Displays Unstable if any of the <br> validation fails. Pipeline stops <br> further execution in that case. |
| <b>Update setupoci.properties</b> | Updates <prefix\>_setupoci.properties <br> with input filename and workflow_type | Displays Failed if any issue during execution |
| <b>Execute setupoci</b> | Executes python code to generate required <br> tfvars files. The console output for this <br> stage is similar to setupoci.py execution via CLI. <br>Multiple options selected will <br> be processed <i>sequentially</i> in this stage. The Excel sheet can be downloaded from **Build artifacts** of the setupoci pipeline. | Displays Failed if any issue occurs  <br> during its execution. Further stages <br> are skipped in that case. |
| <b>Run Import Commands</b> | Based on the workflow_type as 'Export Existing Resources from OCI', <br> this stage invokes execution of <br> import_commands_<resource\>.sh <br> shell scripts which will import the  <br> exported objects into tfstate. import_commands for <br> multiple options selected will be  <br> processed <i>sequentially</i> in this stage. <br><b> This stage is skipped for 'Create New Resources in OCI' workflow </b>| Displays Failed if any issue occurs during its execution.  <br> Further stages are skipped in that case. |
| <b>Git Commit to develop</b> | Commits the terraform_files folder to OCI DevOps GIT Repo develop branch. <br> This will trigger respective terraform pipelines| Pipeline stops further execution if there is nothing to commit. <b>In some cases when tfvars was generated in previous execution, <br> navigate to  **apply** pipeline and trigger that manually </b>|
| <b>Trigger Pipelines</b> | Corresponding terraform/tofu **apply** pipelines <br> are auto triggered based on the service chosen | |

#### a. Download CD3 Excel File
 <a href=../download-excel> <b>Click here for the steps</b></a> to download excel file after successful completion of 'Execute setupoci' stage of the pipeline. The Excel file is available as an artifact for each build of the setupoci pipeline.
  >Note: For create_resources (Greenfield workflow), this will be the same Excel file which was uploaded to create resources in OCI. For export_resoucres (Non-Greenfield workflow), this will be the updated Excel file with exported OCI resource data.

### <b>2. terraform_files Folder</b>

This is equivalent to **```/cd3user/tenancies/<prefix>/terraform_files```** folder on your local system.
The region directories along with all service directories, are present under this terraform_files folder. The toolkit will generate the .tfvars files for all resources under the service directory.
Inside each service directory, pipelines for terraform/tofu **apply** and **destroy** are present.

The pipelines are either triggered automatically from setupoci pipeline or they can be triggered manually by navigating to any service directory path. 


<b><i><b>apply</b> Pipeline Stages</I></b>

|Stage Name      | Description  | Possible Outcomes |
| --------------- | ------------ | ----------------- |
| Checkout SCM | Checks out the latest terraform_files <br> folder from DevOps GIT repo develop branch| |
| Set Environment Variables | Sets the environment variables for region and service name |
| Plan | Runs plan against the <br> checked out code and saves it in tfplan.out | Pipeline stops further execution if the plan shows no changes. <br> Displays Failed if any issue while executing the plan |
| OPA | Runs the above generated plan against <br> Open Policies and displays the violations if any | Displays Unstable if any OPA rule is violated |
| Get Approval | Approval Stage for reviewing the plan. <br> There is 24 hours timeout for this stage. | Proceed - goes ahead with **Apply** stage. <br> Abort - pipeline is aborted and stops further execution |
|Apply | Applies the terraform/tofu configurations | Displays Failed if any issue <br> while executing apply |
|Git Commit to main | Commit to main branch | Stage is skipped if any issue while executing apply |




<b><i>destroy Pipeline Stages</i></b>

|Stage Name      | Description  | Possible Outcomes |
| --------------- | ------------ | ----------------- |
| Checkout SCM | Checks out the latest terraform_files <br> folder from DevOps GIT repo develop branch | |
| Set Environment Variables | Sets the environment variables for region and service name |
| Plan | Runs `terraform plan -destroy` or <br> `tofu plan -destroy` against the checked out code | Displays Failed if any issue in plan output |
| Get Approval | Approval Stage for reviewing the plan. <br> There is 24 hours timeout for this stage. | Proceed - goes ahead with  Destroy stage. <br> Abort - pipeline is aborted and stops furter execution |
|Destroy | Destroys the terraform/tofu configurations | Displays Failed if any issue <br> while executing destroy |
|Git Commit to main | Removes tfvars from respective directory in main branch of repo | Stage is skipped if any issue while executing apply |


### <b>3. Region Based Views</b>
Clicking on any of the views displays all **apply** and **destroy** pipelines in a single screen. This can also be used to trigger the terraform/tofu pipelines. This also includes Global view for global services like RPC.