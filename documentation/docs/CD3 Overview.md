
# **CD3 Automation Toolkit**  
<center><img width="25%" height="30%"  alt="CD3 Logo" src= "/images/CD3-logo.png"> </center>
---

The CD3 toolkit reads input data in the form of CD3 Excel sheet and generates Terraform files which can be used to provision the resources in OCI instead of handling the task through the OCI console manually. The toolkit also reverse engineers the components in OCI back to the Excel sheet and Terraform configuration. The toolkit can be used throughout the lifecycle of tenancy to continuously create or modify existing resources. The generated Terraform code can be used by the OCI Resource Manager or can be integrated into organization's existing devops CI/CD ecosystem.

<br>

<iframe width="100%" height="500" src="https://www.youtube.com/embed/watch?v=TSNu0pUHYsE&list=PLPIzp-E1msrbJ3WawXVhzimQnLw5iafcp&index=1">
</iframe>

<br>
<br>


<u> **CD3 Toolkit Process</u>**


<img width="1049" alt="CD3 Toolkit Process" src="images/CD3-Process.png">

<br>

CD3 Automation toolkit can be used either via CLI or Jenkins.  
📖 Detailed documentation and videos are provided for both options. Please check the left panel for navigation.
Excel Sheet is fed as the input to the toolkit.

**Create resources**

- The filled in input Excel file is processed by the toolkit and terraform *auto.tfvars files are generated for all those resources. 

- The generated terraform files can be used to deploy resources in OCI by generating a terraform plan and approving the plan for apply. 

**Export resources**

- The input Excel (preferably the Blank template) is processed by the toolkit and resources are exported to CD3 Excel template. 

- The toolkit then generates *auto.tfvars from the exported data in Excel file and also generates shell scripts with terraform import commands for all the resources.

- The shell scripts have to be executed in order to have the updated state file to manage the resources further.

**Modify resources**

- Resources created or exported using toolkit can be modified at any point of time using the same Excel file.

<br>



