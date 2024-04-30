# Export and Manage Resources from OCI (Non-Greenfield Workflow)

!!! Note
    Make sure that the service for which export is done does not have existing tfvars/state file.

**Step 1**: 
<br>Choose the Blank CD3 Excel sheet template from [Excel Templates](excel-templates.md).


**Step 2**:
<br>Login to Jenkins URL with user created after initialization and click on setUpOCI pipeline from Dashboard. Click on **Build with Parameters** from left side menu.

<img width="702" height="400" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="../images/jenkinsNGF-1.png"><br>

> **Note:** - Only one user at a time using the Jenkins setup is supported in the current release of the toolkit.

**Step 3**:
<br>Upload the above chosen Excel sheet in **Excel_Template** section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="../images/jenkinsNGF-2.png"><br>
>This will copy the Excel file at `/cd3user/tenancies/<customer_name>` inside the container. It will also take backup of existing Excel on the container by appending the current datetime if same filename is uploaded in multiple executions.


**Step 4:** 
<br>Select the workflow as **Export Existing Resources from OCI (Non-Greenfield Workflow)**. Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows export of Network and Compute.

<img width="554" alt="Screenshot 2024-01-17 at 7 11 42 PM" src="../images/setupocimenu_export_jenkins.jpg"><br>


**Step 5:** 
<br>Specify region and compartment from where the data has to be exported. Multiple options can be selected to export from multiple regions/compartments. If resources have to be exported from all regions/compartments, do not select any option from the dropdown. 
<br>It also asks for service specific filters like display name patterns for compute. Leave empty if no filter is needed.

<img width=500 height=500 alt="Screenshot 2024-01-17 at 7 10 56 PM" src="../images/jenkins_filters.jpg"><br>
<br>Click on **Build** at the bottom.<br>


**Step 6:**
<br>setUpOCI pipeline is triggered and stages are executed as shown below: 

<img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="../images/jenkinsNGF-5.png"><br>
</br>

**Expected Output of 'Execute setUpOCI' stage:**<br>
<ol type="a">
  <li> Overwrites the specific tabs of Excel sheet with the exported resource details from OCI.</li>
  <li> Generates Terraform Configuration files - *.auto.tfvars.</li>
  <li> Generates shell scripts with import commands - <b>tf_import_commands_&lt;resource&gt;_nonGF.sh</b> </li>
</ul>
</ol>

!!! Important

    The updated Excel sheet containing exported data from OCI is present under the **Build artifacts** of the setupoci pipeline. 

    Click on the **Build number** to the left corner of the setupoci pipeline as shown in below image. Under **Build Artifacts**, click on the Excel file name to download it. 

    <img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="../images/setupocistages.jpg">
    <br>
    <img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="../images/buildinfo.jpg">

>Note:
    The updated Excel sheet is also present at ```/cd3user/tenancies/<customer_name>``` inside the container.

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
    

    
!!! note
    - Make sure to execute **Fetch Compartments OCIDs to variables file** from **CD3 Services** in setUpOCI menu at least once. This will ensure that the variables file in outdir is updated with the OCID information of all the compartments.
    - Once the export (including the execution of **tf_import_commands_<resource>_nonGF.sh**) is complete, switch the value of **workflow_type** back to **create_resources**. This allows the toolkit to modify these resources or create new ones on top of them.
