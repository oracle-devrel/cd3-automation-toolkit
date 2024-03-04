# Export Resources from OCI via Jenkins(Non-Greenfield Workflow)

> **Note:**: Please make sure that service for which export is done does not have existing tfvars/state file.

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](ExcelTemplates.md)
Choose **CD3-Blank-template.xlsx** for an empty sheet.

**Step 2**:
<br>Login to Jenkins URL with user created after initialization and click on setUpOCI pipeline from Dashboard. Click on **Build with Parameters** from left side menu.

<img width="702" height="400" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="/images/jenkinsNGF-1.png"><br>

> **Note:** - Only one user at a time using the Jenkins setup is supported in the current release of the toolkit.

**Step 3**:
<br>Upload the above chosen Excel sheet in **Excel_Template** section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="/images/jenkinsNGF-2.png"><br>
>This will copy the Excel file at `/cd3user/tenancies/<customer_name>` inside the container. It will also take backup of existing Excel on the container by appending the current datetime if same filename is uploaded in multiple executions.


**Step 4:** 
<br>Select the workflow as **Export Resources from OCI**(Non-Greenfield Workflow). Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows export of Network and Compute.

<img width="554" alt="Screenshot 2024-01-17 at 7 11 42 PM" src="/images/jenkinsNGF-3.png"><br>


**Step 5:** 
<br>Specify region and compartment from where you want to export the data.
<br>It also asks for service specific filters like display name patterns for compute. Leave empty if no filter is needed.

<img width="835" alt="Screenshot 2024-01-17 at 7 10 56 PM" src="/images/jenkinsNGF-4.png"><br>
<br>Click on **Build** at the bottom.<br>


**Step 6:**
<br>setUpOCI pipeline is triggered and stages are executed as shown below: 

<img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="/images/jenkinsNGF-5.png"><br>
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
  <li> If 'Run Import Commands' stage was successful (ie.. tf_import_commands_&lt;resource&gt;_nonGF.sh ran successfully for all services chosen for export), respective terraform pipelines triggered should have 'Terraform Plan' stage show as 'No Changes'  </li>
</ul>
</ol>
    
<br>
    
> **Note:**<br>
>   Once you have exported the required resources and imported into tfstate, you can use the toolkit to modify them or create new on top of them using 'Create Resources in OCI' workflow.