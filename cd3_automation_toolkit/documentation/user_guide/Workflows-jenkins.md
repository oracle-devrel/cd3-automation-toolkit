# Using the Automation Toolkit via Jenkins

### **Pre-reqs for Jenkins Configuration**
* Validation of createTenancyConfig.py output:
  - jenkins.properties file should have been created under /cd3user/tenancies/jenkins_home  as per input parameters in tenancyConfig.properties<br>
  - An Object Storage bucket should have been created in OCI in the specified compartment to manage remote state. <br>
  - Customer Secret Key should have been configured for the user for S3 credentials of the bucket. <br>
  - A DevOps Project, Repo and Topic should have been created in OCI in the specified compartment. <br>

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

### **Jenkins Initialization**
* Access Jenkins URL using -
  - https://\<IP of the Jenkins Host\>:8443/
    Notes  - 8443 is the port mapped with local system while docker container creation.
           - Network Connectivity should be allowed on this host and port.
  - It will prompt you to create first user to access Jenkins URL. This will be the admin user.
    
  
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Running_SetUpOCI_Pipeline.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
