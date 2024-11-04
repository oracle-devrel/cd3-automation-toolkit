# **Delete prefix and its supporting resources in OCI**
---


Executing createTenancyConfig.py during [Connect Container to OCI](connect-container-to-oci-tenancy.md) creates below components - 

* Config files under /cd3user/tenancies/<prefix\> folder

When using Jenkins, below additional components are created -

* Jenkins files under /cd3user/tenancies/jenkins_home folder. The prefix configurations are added to jenkins.properties and git_config files here.
* OCI Devops Project and repository with name as <prefix\>-automation-toolkit-project to store terraform files
* OCI Topic needed for Devops Project with name as <prefix\>-automation-toolkit-topic
* OCI bucket with name as <prefix\>-automation-toolkit-bucket to store terraform state file.
* Customer Secret Key for the user specified in input tenancyconfig.properties file. This is used as S3 credentials for the bucket storing remote state.

	

**Step 1 - Login (Exec) into the Container**:

* Login to the previously launched container using either [RM Stack](launch-from-rmstack.md) or [Manual Launch](launch-from-local.md).

**Step 2 - Change Directory**:
 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/
  ```


**Step 3 - Execute the script**:

```
python deleteTenancyConfig.py tenancyconfig_<prefix>.properties
```

Execution of above script will remove below components -

* OCI Devops Project and Repository
* OCI Topic
* OCI Bucket
* Customer Secret Key for the user
* Prefix configuration from jenkins.properties and git_config files under /cd3user/tenancies/jenkins_home folder
* /cd3user/tenancies/jenkins_home/jobs/<prefix> folder 
* /cd3user/tenancies/<prefix\> folder

**Step 4 - Restart Jenkins**:

This will remove the prefix from Jenkins Dashboard.

* Command to get Jenkins process id:

```
ps -ef | grep jenkins
```

* Command to kill process:

```
kill -9 <process_id>
```

* Start Jenkins using:

```
/usr/share/jenkins/jenkins.sh &
```
