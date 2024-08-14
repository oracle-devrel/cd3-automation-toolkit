# **CD3 Automation Toolkit**  
---


CD3 stands for **Cloud Deployment Design Deliverable**. The CD3 Automation toolkit enables you to effortlessly Build, Export and Manage OCI (Oracle Cloud Infrastruture) resources by converting Excel templates to fully functional Terraform modules within minutes ⚡️⚡️ . 

Additionally, the toolkit also supports seamless resource management using OCI DevOps GIT service and Jenkins Pipelines.



<br>

<iframe width="100%" height="500" src="https://www.youtube.com/embed/watch?v=TSNu0pUHYsE&list=PLPIzp-E1msrbJ3WawXVhzimQnLw5iafcp&index=1">
</iframe>

<br>
<br>


###<u> **CD3 Toolkit Process</u>**


<img width="2000" height="1000" alt="CD3 Toolkit Process" src="../images/CD3-Process.png">


<br>
The toolkit supports 2 workflows:<br>

**1. Create & Manage Resources in OCI (Greenfield Workflow):**

- Use this workflow when setting up an empty OCI tenancy or creating new resources without the need to modify or use any existing resources in the tenancy.
- The filled in input Excel file is fed to the toolkit and tfvars files are generated for the resources.
- Modifying the same Excel sheet and re running the toolkit will generate updated tfvars files.<br>
- The generated tfvars files can be used to deploy resources in OCI by generating a plan and approving the plan for apply. <br>

**2. Export & Manage Resources in OCI (Non-Greenfield Workflow):**

- Use this workflow to manage existing resources with Terraform/Tofu that were not created using CD3. First, export these resources into CD3 and the state. After the export is complete, switch to the *create_resources* (greenfield) workflow to create new resources or manage existing ones.
- The input Excel (preferably the Blank template) is fed to the toolkit and resources are exported into CD3 Excel template. <br>
- The toolkit then generates tfvars from the exported data in Excel file and also generates shell scripts with import commands for all the resources.<br>
- The shell scripts have to be executed in order to have the updated state file to manage the resources further.<br>
- Modifying the same Excel sheet and re running the toolkit will generate updated tfvars files.<br>


!!! tip
	CD3 Automation toolkit can be used either via CLI or Jenkins.
  
	📖 Detailed documentation and videos are provided for both options. Check the left panel for navigation.


<br>



