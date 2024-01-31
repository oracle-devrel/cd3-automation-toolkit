# Export Resources from OCI via Jenkins(Non-Greenfield Workflow)


**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](/cd3-automation-toolkit/tree/main/cd3_automation_toolkit/example).
Choose **CD3-Blank-template.xlsx** for an empty sheet.

**Step 2**:
<br>Login to Jenkins URL with user created after initialization and click on setUpOCI pipeline from Dashboard. Click on **Build with Parameters** from left side menu.

<img width="702" height="400" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/0674eebb-ca12-4050-97e8-06d67e6cd58f"><br>

>Note - Only one user at a time using the Jenkins setup is supported in the current release of the toolkit.

**Step 3**:
<br>Upload the above chosen Excel sheet in **Excel_Template** section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/3bf84fe7-b317-4120-83db-49f52ed65e95"><br>
>This will copy the Excel file at `/cd3user/tenancies/<customer_name>` inside the container. It will also take backup of existing Excel on the container by appending the current datetime if same filename is uploaded in multiple executions.


**Step 4:** 
<br>Select the workflow as **Export Resources from OCI**(Non-Greenfield Workflow). Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows export of Network and Compute.

<img width="554" alt="Screenshot 2024-01-17 at 7 11 42 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/5c45bc0b-890c-4c93-b129-a15ab3be2d53"><br>


**Step 5:** 
<br>Specify region and compartment from where you want to export the data.
<br>It also asks for service specific filters like display name patterns for compute. Leave empty if no filter is needed.

<img width="835" alt="Screenshot 2024-01-17 at 7 10 56 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/96205ab2-1517-4a79-9bab-72c3b94f6852"><br>
<br>Click on **Build** at the bottom.<br>


**Step 6:**
<br>setUpOCI pipeline is triggered and stages are executed as shown below: 

<img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/d110c5ee-91ae-4e9e-bfb8-607adba026ac"><br>
</br>

**Expected Output of 'Execute setUpOCI' stage:**<br>
<ol type="a">
  <li> Overwrites the specific tabs of Excel sheet with the exported resource details from OCI.</li>
  <li> Generates Terraform Configuration files - *.auto.tfvars.</li>
  <li> Generates shell scripts with import commands - <b>tf_import_commands_&lt;resource&gt;_nonGF.sh</b> </li>
</ul>
</ol>

**Expected Output of 'Run Import Commands' stage:**<br>
<ol type="a">
  <li>Executes shell scripts with import commands(<b>tf_import_commands_&lt;resource&gt;_nonGF.sh</b>) generated in the previous stage </li>
</ul>
</ol>

**Expected Output of Terraform Pipelines:**<br>
<ol type="a">
  <li>Respective pipelines will get triggered automatically from setUpOCI pipeline based on the services chosen for export. You could also trigger manually when required.</li>
  <li> If 'Run Import Commands' stage was successful (ie tf_import_commands_&lt;resource&gt;_nonGF.sh ran successfully for all services chosen for export), respective terraform pipelines triggered should have 'Terraform Plan' stage show as 'No Changes'  </li>
</ul>
</ol>
    
<br>
    
> **Note:**<br>
>   Once you have exported the required resources and imported into tfstate, you can use the toolkit to modify them or create new on top of them using 'Create Resources in OCI' workflow.

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/GF-Jenkins.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/cli_jenkins.md">:arrow_forward: Next</a> |
| :---- | -------: |
  
</div>
