# Using the Automation Toolkit via Jenkins

Jenkins integraton with the toolkit is provided to jump start your journey with CI/CD for IaC in OCI. A beginner level of understanding of Jenkins is required.

## **Pre-reqs for Jenkins Configuration**
* The configurations are done when you execute createTenancyConfig.py. Please validate them:
  - jenkins.properties file should have been created under /cd3user/tenancies/jenkins_home  as per input parameters in tenancyConfig.properties<br>
  - An Object Storage bucket should have been created in OCI in the specified compartment to manage tfstate remotely. <br>
  - Customer Secret Key should have been configured for the user for S3 credentials of the bucket. <br>
  - A DevOps Project, Repo and Topic should have been created in OCI in the specified compartment to store terraform_files. <br>


## **Bootstrapping of Jenkins in the toolkit**

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

* Access Jenkins URL using -
  - https://\<IP of the Jenkins Host\>:\<Port>/ <br>
    > Notes:
     > - \<Port> is the port mapped with local system while docker container creation Eg: 8443.
     > -  Network Connectivity should be allowed on this host and port.
  - It will prompt you to create first user to access Jenkins URL. This will be the admin user.
  - Once you login, Jenkins Dashbord will be displayed.
    
     
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Automation Toolkit via CLI</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Intro-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
