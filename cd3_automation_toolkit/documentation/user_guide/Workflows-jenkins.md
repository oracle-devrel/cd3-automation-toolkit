# Using the Automation Toolkit via Jenkins

### ** Jenkins Configuration**
* Validation of createTenancyConfig.py output:
  - jenkins.properties file should have been created under /cd3user/tenancies/jenkins_home  as per input parameters in tenancyConfig.properties<br>
  - An Object Storage bucket should have been created in OCI in the specified compartment to manage remote state. <br>
  - Customer Secret Key should have been configured for the user for S3 credentials of the bucket. <br>
  - A DevOps Project, Repo and Topic should have been created in OCI in the specified compartment. <br>

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

* Access Jenkins URL using -
  - https://<IP of the Jenkins Host>:8443/
  - It will prompt you to create first user to access Jenkins URL. This will be the admin user.
    
  
  
