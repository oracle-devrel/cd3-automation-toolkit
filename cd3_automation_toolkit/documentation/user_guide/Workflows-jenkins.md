# Using the Automation Toolkit via Jenkins

### **Pre-reqs for Jenkins Configuration**
* Validation of createTenancyConfig.py output:
  - jenkins.properties file should have been created under /cd3user/tenancies/jenkins_home  as per input parameters in tenancyConfig.properties<br>
  - An Object Storage bucket should have been created in OCI in the specified compartment to manage tfstate remotely. <br>
  - Customer Secret Key should have been configured for the user for S3 credentials of the bucket. <br>
  - A DevOps Project, Repo and Topic should have been created in OCI in the specified compartment to store terraform_files. <br>

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

### **Initialization of Jenkins**
* Access Jenkins URL using -
  - https://\<IP of the Jenkins Host\>:8443/
    Notes  - 8443 is the port mapped with local system while docker container creation.
           - Network Connectivity should be allowed on this host and port.
  - It will prompt you to create first user to access Jenkins URL. This will be the admin user.
  - Once you login, here is the Jenkins dashboard:
    <br>
     <img width="1486" alt="Screenshot 2024-01-16 at 10 52 07 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/70213341/4534834b-3ad6-427b-8f13-121c136054d3">

### **Introduction of Jenkins**

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Automation Toolkit via CLI</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField-Jenkins.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
