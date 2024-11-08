# **Delete prefix and its supporting resources in OCI**
---

Users can delete an existing prefix if they are not using it anymore to ensure no prefix-specific residual resources or components remain and to avoid naming conflicts in future executions. This is also beneficial for users who want to re-run ```createTenancyConfig.py``` with the same prefix after an unsuccessful execution.

<br>

**Resources created with createTenancyConfig.py execution**

When executing createTenancyConfig.py during <a href="../connect-container-to-oci-tenancy"><u>Connect Container to OCI</u></a>, the below components are created:

* Config files under ```/cd3user/tenancies/<prefix>``` folder


**Additional Resources created with Jenkins**

When using Jenkins, the following additional components are created:

* Jenkins files under ```/cd3user/tenancies/jenkins_home``` folder. The prefix configurations are added to ```jenkins.properties``` and ```git_config``` files.
* OCI Devops Project and repository named ```<prefix>-automation-toolkit-project``` to store terraform files
* OCI Topic needed for Devops Project named ```<prefix>-automation-toolkit-topic```
* OCI bucket named ```<prefix>-automation-toolkit-bucket``` to store terraform state file.
* Customer Secret Key for the user specified in tenancyconfig.properties file. This is used as S3 credential for the bucket storing remote state.

<br>

**Steps to Delete the above prefix-specific Resources**


**Step 1 - Login (Exec) into the Container**:

* Login to the existing CD3 container using either <a href="../launch-from-rmstack"><u>RM Stack</u></a> or <a href="../launch-from-local"><u>Manual Launch</u></a>.

**Step 2 - Navigate to user-scripts folder**:
 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/
  ```


**Step 3 - Run the Deletion Script**:

```
python deleteTenancyConfig.py tenancyconfig_<prefix>.properties
```

This script will remove:

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
