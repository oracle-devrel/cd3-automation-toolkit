# Using the Automation Toolkit via Jenkins

Jenkins integraton with the toolkit is provided to jump start your journey with CI/CD for IaC in OCI. A beginner level of understanding of Jenkins is required.

## **Pre-reqs for Jenkins Configuration**
* The configurations are done when you execute createTenancyConfig.py in [Connect container to OCI Tenancy](/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md). Please validate them:
  - jenkins.properties file is created under _/cd3user/tenancies/jenkins\_home_  as per input parameters in tenancyConfig.properties<br>
  - An Object Storage bucket is created in OCI in the specified compartment to manage tfstate remotely. <br>
  - Customer Secret Key is configured for the user for S3 credentials of the bucket. <br>
  - A DevOps Project, Repo and Topic are created in OCI in the specified compartment to store terraform_files. GIT is configured on the container with config file at ```/cd3user/.ssh/config``` <br>


## **Bootstrapping of Jenkins in the toolkit**

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

* Access Jenkins URL using -
  - https://\<IP of the Jenkins Host\>:\<Port>/ <br>
    > Notes:
     > - \<Port> is the port mapped with local system while docker container creation Eg: 8443.
     > -  Network Connectivity should be allowed on this host and port. Please make sure to use private server or bastion with restricted public access.
  - It will prompt you to create first user to access Jenkins URL. This will be the admin user.
  - The Automation Toolkit only supports a single user Jenkins setup in this release.
  - Once you login, Jenkins Dashbord will be displayed.
    
     
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Automation Toolkit via CLI</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Intro-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
