# **Create and Manage Resources in OCI (Greenfield Workflow)**

## Execute setUpOCI Pipeline

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](excel-templates.md).
Fill the CD3 Excel with appropriate values.


**Step 2**:
<br>Login to Jenkins URL with the user created after initialization and click on **setUpOCI pipeline** from Dashboard. Click on **'Build with Parameters'** from left side menu.

<img width="600" height="350" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="../images/jenkinsGF-1.png">

!!! note
     Only one user at a time using the Jenkins setup is supported in the current release of the toolkit.


**Step 3**:
<br>Upload the above filled Excel sheet in **Excel_Template** section.

<img width="348" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="../images/jenkinsGF-2.png"><br>

!!! info 
    This will copy the Excel file at `/cd3user/tenancies/<customer_name>` inside the container. It will also take backup of existing Excel on the container by appending the current datetime if same filename is uploaded in multiple executions.


**Step 4:** 
<br>Select the workflow as **Create New Resources in OCI(Greenfield Workflow)**. Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br> Check out [this](multiple-services-jenkins.md) while selcting multiple options simultaneously.
<br>Below screenshot shows creation of Compartments (under Identity) and Tags.

<img width="920" height="300" alt="Screenshot 2024-01-17 at 12 04 15 PM" src="../images/setupocimenu_create_jenkins.jpg"><br>

Click on **Build** at the bottom.


**Step 5:** 
<br>setUpOCI pipeline is triggered and stages are executed as shown below.<br>
This will run the python script to generate the terraform auto.tfvars.  Once created, it will commit to the OCI Devops GIT Repo and then it will also launch terraform-apply pipelines for the services chosen (Stage:phoenix/identity and Stage:phoenix/tagging in the below screenshot).

<img width="1000" height="400" alt="Screenshot 2024-01-17 at 11 57 14 AM" src="../images/jenkinsGF-4.png">

## Execute terraform Pipelines
Terraform pipelines are auto triggered parallely from setUpOCI pipeline based on the services selected (the last two stages in above screenshot show trigger of terraform pipelines). <br>

**Step 1**: 

Click on 'Logs' for Stage: phoenix/identity and click on the pipeline link.
<img width="1402" height="400" alt="Screenshot 2024-01-17 at 11 58 15 AM" src="../images/jenkinsGF-5.png"><br>
> ***Note - Navigating to Dashboard displays pipelines that are in running state at the bottom left corner.***<br>
> ***Or you can also navigate from Dashboard using the region based view (Dashboard -> phoenix View -> service specific pipeline)***<br>
<br>
> ***In this example it would be:*** <br>
> &emsp; ***terraform_files » phoenix » tagging » terraform-apply*** <br>
> &emsp; ***terraform_files » phoenix » identity » terraform-apply*** <br>

**Step 2**: 
<br>Stages of the terraform pipeline for apply are shown below:

<img width="830" height="450" alt="Screenshot 2024-01-17 at 12 01 42 PM" src="../images/jenkinsGF-6.png"><br>

**Step 3**:
<br>Review Logs for Terraform Plan and OPA stages by clicking on the stage and then 'Logs'. 

<img width="1503" alt="Screenshot 2024-01-17 at 12 13 57 PM" src="../images/jenkinsGF-7.png"><br>


**Step 4**: 
<br>'Get Approval' stage has timeout of 24 hours, if no action is taken the pipeline will be aborted after 24 hours. Click on this stage and click 'Proceed' to proceed with terraform apply or 'Abort' to cancel the terraform apply.


<img width="920" height="300" alt="Screenshot 2024-01-17 at 12 04 15 PM" src="../images/jenkinsGF-8.png"><br>


**Step 5**:
<br>Below screenshot shows Stage View after clicking on 'Proceed'. Login to the OCI console and verify that resources got created as required.

<img width="702" height="360" alt="Screenshot 2024-01-17 at 12 13 15 PM" src="../images/jenkinsGF-9.png"><br>

**Step 6**:
<br>Similarly click on 'Logs' for Stage: phoenix/tagging and click on the pipeline link and 'Proceed' or 'Abort' the terraform apply<br><br>


<br><br>

<div align='center'></div>
