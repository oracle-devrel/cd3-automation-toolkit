# Using the Automation Toolkit with Jenkins

Jenkins integration with the toolkit is provided to jump start your journey with CI/CD for IaC in OCI. A beginner level of understanding of Jenkins is required.

## **Pre-reqs for Jenkins Configuration**
* The configurations are done when you execute createTenancyConfig.py in [Connect container to OCI Tenancy](connect-container-to-oci-tenancy.md). Please validate them:
  - jenkins.properties file is created under _/cd3user/tenancies/jenkins\_home_  as per input parameters in tenancyConfig.properties<br>
  - An Object Storage bucket is created in OCI in the specified compartment to manage tfstate remotely. <br>
  - Customer Secret Key is configured for the user for S3 credentials of the bucket. <br>
  - A DevOps Project, Repo and Topic are created in OCI in the specified compartment to store terraform_files. GIT is configured on the container with config file at ```/cd3user/.ssh/config``` <br>


## **Bootstrapping of Jenkins in the toolkit**

* Execute below cmd to start Jenkins - <br>
```/usr/share/jenkins/jenkins.sh &```

* Access Jenkins URL using: ```https://<IP of the Jenkins Host>:<Port>``` 
  <br>
!!! note
      - ```<Port>``` is the port mapped with local system while docker container creation Eg: 8443.
      -  Network Connectivity should be allowed on this host and port.
      -  Please make sure to use a private server or a bastion connected server with restricted access(i.e. not publicly available).

  - It will prompt you to create first user to access Jenkins URL. This will be the admin user.
  - The Automation Toolkit only supports a single user Jenkins setup in this release.
  - Once you login, Jenkins Dashbord will be displayed.
