# Using the Automation Toolkit with Jenkins

Jenkins integration with the toolkit is provided to jump start your journey with CI/CD for IaC in OCI. A beginner level of understanding of Jenkins is required.

## **Pre-reqs for Jenkins Configuration**

The configurations are done when executing createTenancyConfig.py in [Connect container to OCI Tenancy](connect-container-to-oci-tenancy.md). Here are the validation steps:

  - jenkins.properties file is created under ```/cd3user/tenancies/jenkins_home```  as per input parameters in tenancyconfig.        properties<br>
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

  - It will prompt to create the first user to access Jenkins URL. This will be the admin user.
  - The Automation Toolkit only supports a single user Jenkins setup in this release.
  - After logging in, Jenkins Dashboard will be displayed.

## **High Level Steps to use toolkit with Jenkins**

1. Login to the CD3 Container.

2. Check out [CD3 Toolkit Process](cd3-overview.md#cd3-toolkit-process) for workflows supported by the toolkit and choose the workflow.

3. Use one of the templates from [Excel Templates](excel-templates.md) based on the workflow chosen.
4. Execute setUpOCI pipeline from [Jenkins Dashboard](jenkinsintro.md).
