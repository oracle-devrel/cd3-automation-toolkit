# Create resources in OCI via Jenkins(Greenfield Workflow)

## Execute setUpOCI Pipeline
Below are the steps that will help to execute setUpOCI pipeline to create new resources in tenancies:

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide./RunningAutomationToolkit.md#excel-sheet-templates)
Fill the CD3 Excel with appropriate values specific to the client.


**Step 2**:
<br>Login to Jenkins URL with user created after initialization and click on setUpOCI pipeline from Dashboard. Click on 'Build with Parameters' from left side menu.

<img width="600" height="350" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/4e298946-6fb1-477b-9915-96a50c777d99">


**Step 3**:
<br>Upload the above filled Excel sheet in **Excel_Template** section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/9b7916aa-9dbb-43f8-8758-5f9c14481006"><br>


**Step 4:** 
<br>Select the workflow as 'Create Resources in OCI(Greenfield Workflow). Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows creation of Compartments (under Identity) and Tags.

<img width="395" alt="Screenshot 2024-01-16 at 2 44 38 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/c55f0486-fba4-4c61-9f05-224b128e0143">

Click on **Build** at the bottom.


**Step 5:** 
<br>setUpOCI pipeline is triggered and stages are executed as shown below:

<img width="700" height="300" alt="Screenshot 2024-01-17 at 11 57 14 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/b5183bc7-f984-46f9-88f9-f7281e9963fb">


## Execute terraform Pipelines
Terraform pipelines are auto triggered parallely based on the services selected.<br><br>
**Step 1**: 
<br>Click on 'Logs' for Stage: phoenix/identity and click on the pipeline link.
> ***Note - Clicking on Dashboard also shows pipelines that are in running state.***<br>
> ***Or you can also navigate from Dashboard -> terraform_files -> phoenix -> identity -> terraform_apply***

<img width="1402" height="400" alt="Screenshot 2024-01-17 at 11 58 15 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/9d14e5ae-92ec-4fea-9ad0-4866b17737a1"><br>


**Step 2**: 
<br>Stages of the terraform pipeline for apply are shown below:

<img width="920" height="430" alt="Screenshot 2024-01-17 at 12 01 42 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/934bb23d-58d2-4269-88b0-08ffd21c1a61"><br>


**Step 3**:
<br>Review Logs for Terraform Plan and OPA stages by clicking on the stage and then 'Logs'. 

<img width="1503" alt="Screenshot 2024-01-17 at 12 13 57 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/ad3f0081-a9ea-49f3-99f5-82f24131b7ac"><br>


**Step 4**: 
<br>Click on Get Approval stage and click 'Proceed' to proceed with terraform apply or 'Abort' the terraform apply.

<img width="920" height="300" alt="Screenshot 2024-01-17 at 12 04 15 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/4082f752-ae72-407e-8b63-5728d4b5b5a8"><br>


**Step 5**:
<br>Below screenshot shows Stage View after clicking on 'Proceed'. You can login to the OCI console and verify that resources got created as required.

<img width="702" height="360" alt="Screenshot 2024-01-17 at 12 13 15 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/78f2b3fb-ceef-4f72-874a-35bce1170c56"><br>

**Step 6**:
<br>Similarly click on 'Logs' for Stage: phoenix/tagging and click on the pipeline link and 'Proceed' or 'Abort' the terraform apply



<br><br>

<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Running_SetUpOCI_Pipeline.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
