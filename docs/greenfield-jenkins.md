# **Create and Manage Resources in OCI (Greenfield Workflow)**

## Execute setUpOCI Pipeline

**Step 1**: 
<br>Choose the appropriate CD3 Excel sheet template from [Excel Templates](excel-templates.md).
Fill the CD3 Excel with appropriate values.


**Step 2**:
<br>Login to Jenkins URL with user created after initialization. On the dashboard, a folder with **<prefix\>** name is present. 
Click on it. It has the corresponding **setupoci pipeline** and **terraform_files** folder. 

Click on the setupoci pipeline and select **Build with Parameters** from left side menu.

<img width="1600" height="550" alt="Screenshot 2024-01-16 at 10 56 42 AM" src="../images/jenkinsGF-1.jpg">

!!! note
     Only one user at a time using the Jenkins setup is supported in the current release of the toolkit.


**Step 3**:
<br>Upload the above filled Excel sheet in **Excel_Template** section.

<img width="1000" height="500" alt="Screenshot 2024-01-16 at 11 04 47 AM" src="../images/jenkinsGF-2.jpg"><br>

!!! info 
    This will copy the Excel file at `/cd3user/tenancies/<prefix>` inside the container. It will also take backup of existing Excel on the container by appending the current datetime if same filename is uploaded in multiple executions.


**Step 4:** 
<br>Select the workflow as **Create New Resources in OCI(Greenfield Workflow)**. Choose single or multiple MainOptions as required and then corresponding SubOptions.
<br> Check out <b>[this](multiple-services-jenkins.md)</b> while selecting multiple options simultaneously.
<br>Below screenshot shows creation of Compartments (under Identity) and Tags (under Governance).

<img width="520" height="200" alt="Screenshot 2024-01-17 at 12 04 15 PM" src="../images/demo_setupocimenu_jenkins_create.jpg"><br>

Click on **Build** at the bottom.


**Step 5:** 
<br>setUpOCI pipeline is triggered and stages are executed as shown below.<br>
This will run the python script to generate the terraform auto.tfvars.  Once created, it will commit to the OCI Devops GIT Repo and then it will also launch terraform **apply** pipelines for the services chosen (Stage:ashburn/identity and Stage:ashburn/tagging in the below screenshot).

<img width="1000" height="400" alt="Screenshot 2024-01-17 at 11 57 14 AM" src="../images/jenkinsGF-4.jpg">

## Execute terraform Pipelines
Terraform pipelines are auto triggered parallely from setUpOCI pipeline based on the services selected (the last two stages in above screenshot show trigger of terraform pipelines). <br>

**Step 1**: 

Click on 'Logs' for Stage: ashburn/identity and click on the pipeline link.
<img width="1402" height="400" alt="Screenshot 2024-01-17 at 11 58 15 AM" src="../images/jenkinsGF-5.jpg"><br>
> ***Note - Navigating to Dashboard displays pipelines that are in running state at the bottom left corner.***<br>
> ***Or you can also navigate from Dashboard using the region based view (Dashboard --> prefix --> ashburn View --> service specific pipeline)***<br>
<br>
> ***In this example it would be:*** <br>
> &emsp; ***cd3toolkit-demo » terraform_files » ashburn » identity » apply*** <br>
> &emsp; ***cd3toolkit-demo » terraform_files » ashburn » tagging » apply*** <br>

**Step 2**: 
<br>Stages of the terraform pipeline for apply are shown below:

<img width="830" height="450" alt="Screenshot 2024-01-17 at 12 01 42 PM" src="../images/jenkinsGF-6.jpg"><br>

**Step 3**:
<br>Review Logs for Terraform Plan and OPA stages by clicking on the stage and then 'Logs'. 

<img width="1503" alt="Screenshot 2024-01-17 at 12 13 57 PM" src="../images/jenkinsGF-7.jpg"><br>


**Step 4**: 
<br>'Get Approval' stage has timeout of 24 hours, if no action is taken the pipeline will be aborted after 24 hours. Click on this stage and click 'Proceed' to proceed with terraform apply or 'Abort' to cancel the terraform apply.


<img width="920" height="300" alt="Screenshot 2024-01-17 at 12 04 15 PM" src="../images/jenkinsGF-8.jpg"><br>


**Step 5**:
<br>Below screenshot shows Stage View after clicking on 'Proceed'. Login to the OCI console and verify that resources got created as required.

<img width="920" height="360" alt="Screenshot 2024-01-17 at 12 13 15 PM" src="../images/jenkinsGF-9.jpg"><br>

**Step 6**:
<br>Similarly click on 'Logs' for Stage: ashburn/tagging and click on the pipeline link and 'Proceed' or 'Abort' the terraform apply<br><br>


<br><br>

<div align='center'></div>
