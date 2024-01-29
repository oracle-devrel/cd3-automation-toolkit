    
## **Introduction to Jenkins with the toolkit**

### Jenkins Dashbord
<img width="1486" alt="Screenshot 2024-01-16 at 10 52 07 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/cbf61a8e-216f-4667-9351-d568a0a38453">

1. setUpOCI Pipeline
2. terraform_files Folder
3. Region based Views (including Global directory)

The process of invocation/execution of these stages is explained in the next pages.

### 1. setUpOCI Pipeline

This is equivalent to running *setUpOCI.py* from CLI. Below table shows the stages executed in this pipeline along with their description:

#### setUpOCI Pipeline Stages :

|Stage Name      | Description  | Possible Outcomes |
| --------------- | ------------ | ----------------- |
| <b>Validate Input Parameters</b> | Validates input file name/size, selected parameters | Displays Unstable if any of the validation fails. Pipeline stops further execution in that case. |
| <b>Update setUpOCI.properties</b> | Updates <customer_name>_setUpOCI.properties with input filename and workflow_type | Displays Failed if any issue during execution |
| <b>Execute setUpOCI</b> | Executes python code to generate required tfvars files. The console output for this stage is similar to setUpOCI.py execution via CLI. <br>Multiple options selected will be processed <i>sequentially</i> in this stage. | Displays Failed if any issue occurs during its execution. Further stages are skipped in that case. |
| <b>Run Import Commands</b> | Based on the workflow_type as 'Export Resources from OCI', this stage invokes execution of tf_import_commands_\<resource\>_nonGF.sh shell scripts which will import the exported objects into tfstate. tf_import_commands for multiple options selected will be processed <i>sequentially</i> in this stage. <br><b> This stage is skipped for 'Create Resources in OCI' workflow </b>| Displays Failed if any issue occurs during its execution. Further stages are skipped in that case. |
| <b>Git Commit</b> | Commits the terraform_files folder to OCI DevOps GIT Repo. This will trigger respective terraform_pipelines| Pipeline stops further execution if there is nothing to commit. <b>In some cases when tfvars was generated in previous execution, you can navigate to terrafom-apply pipeline and trigger that manually </b>|
| <b>Trigger Terraform Pipelines</b> | Corresponding terraform apply pipelines are auto triggered based on the service chosen | |

### 2. terraform_files Folder

This is equivalent to */cd3user/tenancies/<customer_name>/terraform_files* folder on your local system.
You will see region directories inside this and all service directories further inside the region directories.
Inside each service directory, you will see pipelines for **terraform-apply** and **terraform-destroy**.

You can navigate to any service directory path and invoke the terraform-apply pipeline.

#### terraform-apply Pipeline Stages :

|Stage Name      | Description  | Possible Outcomes |
| --------------- | ------------ | ----------------- |
| Checkout SCM | Checks out the latest terraform_files folder from DevOps GIT repo | |
| Terraform Plan | Runs terraform plan against the checked out code and saves it in tfplan.out | Pipeline stops further execution if terraform plan shows no changes. Displays Failed if any issue while executing terraform plan |
| OPA | Runs the above genrated terraform plan against Open Policies and displays the violations if any | Displays Unstable if any OPA rule is violated |
| Get Approval | Approval Stage for reviewing the terraform plan. There is 24 hours timeout for this stage. | Proceed - goes ahead with Terraform Apply stage. <br> Abort - pipeline is aborted and stops furter execution |
|Terraform Apply | Applies the terraform configurations | Displays Failed if any issue while executing terraform apply |

### 3. Region Based Views
When you click on any of the view, it displays all terraform-apply and terraform-destroy pipelines in single screen. This can also be used to trigger the terraform pipelines. This also includes Global view for global services like RPC

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows-jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>

