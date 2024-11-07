# Export and Manage Resources from OCI (Non-Greenfield Workflow)

!!! important
    - Toolkit will **over-write** the data in specific tabs of CD3 Excel sheet with exported content from OCI while the other tabs remain intact.
    - Differential state import of the objects will be performed, i.e., the import statements will be generated only for the objects not already present in state file.

**Step 1**: 
<br>Choose the Blank CD3 Excel sheet template from <a href="../excel-templates"><u>Excel Templates</u></a>.


**Step 2**:
<br>Login to Jenkins URL with user created after initialization. On the dashboard, a folder with **<prefix\>** name is present. 
Click on it. It has the corresponding **setupoci pipeline** and **terraform_files** folder. 

Click on the setupoci pipeline and select **Build with Parameters** from left side menu.


<img width="920" height="400" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="../images/jenkinsNGF-1.jpg"><br>

> **Note:** - Only one user at a time using the Jenkins setup is supported in the current release of the toolkit.

**Step 3**:
<br>Upload the above chosen Excel sheet in **Excel_Template** section.

<img width="920" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="../images/jenkinsNGF-2.jpg"><br>
>This will copy the Excel file at `/cd3user/tenancies/<prefix>` inside the container. It will also take backup of existing Excel on the container by appending the current datetime if same filename is uploaded in multiple executions.


**Step 4:** 
<br>Select the workflow as **Export Existing Resources from OCI (Non-Greenfield Workflow)**. Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br>Below screenshot shows export of Network and Compute.

<img width="554" alt="Screenshot 2024-01-17 at 7 11 42 PM" src="../images/demo_setupocimenu_jenkins_export.jpg"><br>


**Step 5:** 
<br>Specify region and compartment from where the data has to be exported. Multiple options can be selected to export from multiple regions/compartments. If resources have to be exported from all regions/compartments, do not select any option from the dropdown. 
<br>It also asks for service specific filters like display name patterns for compute. Leave empty if no filter is needed.

<img width=500 height=500 alt="Screenshot 2024-01-17 at 7 10 56 PM" src="../images/jenkins_filters.jpg"><br>
<br>Click on **Build** at the bottom.<br>


**Step 6:**
<br>setUpOCI pipeline is triggered and stages are executed as shown below: 

<img width="1505" alt="Screenshot 2024-01-17 at 9 37 22 PM" src="../images/jenkinsNGF-5.jpg"><br>
</br>

**Expected Output of 'Execute setUpOCI' stage:**<br>
<ol type="a">
  <li> Overwrites the specific tabs of Excel sheet with the exported resource details from OCI. Here are the <a href=../download-excel> <b>steps</b></a> to download the exported Excel file. </li>
  
  <li> Generates Configuration files - *.auto.tfvars.</li>
  <li> Generates shell scripts with import commands - <b>import_commands_&lt;resource&gt;.sh</b> </li>
</ul>
</ol>
 

>Note:
    The updated Excel sheet is also present at ```/cd3user/tenancies/<prefix>``` inside the container.

**Expected Output of 'Run Import Commands' stage:**<br>
<ol type="a">
  <li>Executes shell scripts with import commands(<b>import_commands_&lt;resource&gt;.sh</b>) generated in the previous stage </li>
</ul>
</ol>

**Expected Output of terraform/tofu Pipelines:**<br>
<ol type="a">
  <li>Respective pipelines will get triggered automatically from setUpOCI pipeline based on the services chosen for export. You could also trigger manually when required.</li>
  <li> If 'Run Import Commands' stage was successful (ie.. import_commands_&lt;resource&gt;.sh ran successfully for all services chosen for export), respective pipelines triggered should have 'Plan' stage show as 'No Changes'  </li>
</ul>
</ol>
    

    
!!! note
    - Make sure to execute **Fetch Compartments OCIDs to variables file** from **CD3 Services** in setUpOCI menu at least once. This will ensure that the variables file in outdir is updated with the OCID information of all the compartments.
    - Once the export (including the execution of **import_commands_<resource>.sh**) is complete, switch the value of **workflow_type** back to **create_resources**. This allows the toolkit to modify these resources or create new ones on top of them.
