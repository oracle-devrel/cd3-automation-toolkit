# Create resources in OCI via Jenkins(Greenfield Workflow)

## Execute setUpOCI pipeline
Below are the steps that will help to execute setUpOCI pipeline to create new resources in tenancies:

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide./RunningAutomationToolkit.md#excel-sheet-templates)
Fill the CD3 Excel with appropriate values specific to the client.


**Step 2**:
<br>Login to Jenkins URL with user created after initialization and click on setUpOCI pipeline from Dashboard. Click on 'Build with Parameters' from left side menu.
<img width="872" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/7c71d75d-b3cd-478c-8275-b6385e3b427b">


**Step 3**:
<br>Upload the above filled in excel sheet in Excel_Template section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/25d720c5-fa23-49a4-b80e-663eae179753"><br>

**Step 4:** 
<br>Select the workflow as 'Create Resources in OCI(Greenfield Workflow). Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows creation of Compartments (under Identity) and Tags.

<img width="395" alt="Screenshot 2024-01-16 at 2 44 38 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/ca32dec6-3193-4593-990e-694a78109e28">

Click on Build at the bottom.


**Step 5:** 
<br>setUpOCI pipline is triggered and stages are executed as shown below:
<img width="1202" alt="Screenshot 2024-01-17 at 11 57 14 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/2eeb8419-82ca-4b7b-97fa-095dd9d4f4c3">


## Execute terraform pipelines
Terraform pipelines are auto triggered parallely based on the services selected.<br><br>
**Step 1**: 
<br>Click on 'Logs' for Stage: phoenix/identity and click on the pipeline link.
> ***Note - Clicking on Dashboard also shows pipelines that are in running state.***<br>
> ***Or you can also navigate from Dashboard -> terraform_files -> phoenix -> identity -> terraform_apply***


<img width="1502" alt="Screenshot 2024-01-17 at 11 58 15 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/5ac32eee-c6f4-4bb4-9373-639c2637f3c2"><br>

**Step 2**: 
<br>Stages of the the terraform pipeline for apply are shown below:
<img width="920" alt="Screenshot 2024-01-17 at 12 01 42 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/cd343b15-5df1-4b9c-8bb8-c5b1a0eafe85">

**Step 3**:
<br>Review Logs for Terraform Plan and OPA stages by clikcing on the stage and then 'Logs'. 
<img width="1503" alt="Screenshot 2024-01-17 at 12 13 57 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/30672f82-74ef-4821-9072-b5edeb33bd72">


**Step 4**: 
<br>Click on Get Approval stage and click 'Proceed' to proceed with terraform apply or 'Abort' the terraform apply.
<img width="920" alt="Screenshot 2024-01-17 at 12 04 15 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/c2e588c7-946b-4b66-b0cc-3d7dba72447e">

**Step 5**:
<br>Below screenshot shows Stage View after clicking on 'Proceed'. You can login to the OCI console and verify that resources got created as required.
<img width="902" alt="Screenshot 2024-01-17 at 12 13 15 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/9449dcdf-662d-4f8e-a9fe-90a084cb6fe4">

**Step 6**:
<br>Similarly click on 'Logs' for Stage: phoenix/tagging and click on the pipeline link and 'Proceed' or 'Abort' the terraform apply



<br><br>

<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Running_SetUpOCI_Pipeline.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
