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
<br>Upload the filled in excel sheet in Excel_Template section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/25d720c5-fa23-49a4-b80e-663eae179753">

**Step 4:** 
Select the workflow as 'Create Resources in OCI(Greenfield Workflow). Choose single or multiple Main Options and then corresponding SubOptions as required.
<br>Below screenshot shows creation of Compartments (under Identity) and Tags.

<img width="395" alt="Screenshot 2024-01-16 at 2 44 38 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/ca32dec6-3193-4593-990e-694a78109e28">

Click on Build.

**Step 5:** 
setUpOCI pipline is triggered and stages are executed as shown below:
<img width="1203" alt="Screenshot 2024-01-16 at 3 25 55 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/dbc39fdd-422e-4ab3-a95b-10a84e80a441">

## Execute terraform pipelines
Terraform pipelines are auto triggered based on the services selected. Click on Logs for Stage: phoenix/identity and click on the pipeline link
<img width="1511" alt="Screenshot 2024-01-16 at 3 27 49 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/7c434f24-7da9-4e15-b0ff-3750f6ca4b39">

 <br><br>

<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Running_SetUpOCI_Pipeline.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
