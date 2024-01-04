# Using the Automation Toolkit via Jenkins

### **Start Jenkins**
<br>
* Validation of createTenancyConfig.py output:

<br>
  - jenkins.properties file should have been created under /cd3user/tenancies/jenkins_home <br>
  - An OS bucket should have been created in OCI in the specified compartment to manage remote state. <br>
  - Customer Secret Key should have been configured for the user for S3 credentials of the bucket. <br>
  - A DevOps project, repo and Topic should have been created in OCI in the specified compartment. <br>

<br>
* Execute below cmd to start Jenkins -
<br>
```/usr/share/jenkins/jenkins.sh &```
