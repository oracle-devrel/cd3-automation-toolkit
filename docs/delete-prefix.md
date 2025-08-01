# **Delete prefix and its supporting resources in OCI**
---

 Users can delete an existing prefix if they are not using it anymore to ensure no prefix-specific residual resources or components remain and also to avoid naming conflicts in future executions.<br>
🔁  This is also beneficial for users who want to re-run ```createTenancyConfig.py``` with the same prefix after an unsuccessful execution.

<br>


<span style="color: teal;"><b>Resources created with createTenancyConfig.py execution:</b></span>

When executing createTenancyConfig.py during <a href="../connect-container-to-oci-tenancy"><u>Connect Container to OCI</u></a>, the following components are created:

* Config files under ```/cd3user/tenancies/<prefix>``` folder

<br>


<span style="color: teal;"><b>Additional Resources created with Jenkins:</b></span>

When using Jenkins, the following additional components are created:


  <span style="color: teal;"><b>📁 On the VM</b></span>

  * Jenkins files under ```/cd3user/tenancies/jenkins_home``` folder. 
  * Updated config files:
      * ```jenkins.properties```
      * ```git_config``` (includes prefix configs)



  <span style="color: teal;"><b>☁️ On OCI:</b></span>

  * DevOps Project and Code Repository
      ```<prefix>-automation-toolkit-project```

  * OCI Topic for DevOps notifications
      ```<prefix>-automation-toolkit-topic```

  * OCI Object Storage Bucket for Terraform state
      ```<prefix>-automation-toolkit-bucket```

  * Customer Secret Key
    Used as S3 credential for the bucket storing remote state, tied to the user in ```tenancyconfig.properties```.



<br>


<h3 style="color: crimson; font-weight: bold;"> Steps to Delete the above prefix-specific Resources</h3> <br>



<span style="color: teal;"><b>Step 1 - Login (Exec) into the Container:</b></span>

* Login to the existing CD3 container using either <a href="../launch-from-rmstack"><u>RM Stack</u></a> or <a href="../launch-from-local"><u>Manual Launch</u></a>.

<br>

<span style="color: teal;"><b>Step 2 - Navigate to user-scripts folder:</b></span>
 
  ```
  cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/
  ```

<br>

<span style="color: teal;"><b>Step 3 - Run the Deletion Script:</b></span>

```
python deleteTenancyConfig.py tenancyconfig_<prefix>.properties
```

This script will remove :

* OCI Devops Project and Repository
* OCI Topic
* OCI Bucket
* Customer Secret Key for the user
* Prefix configuration from jenkins.properties and git_config files under ```/cd3user/tenancies/jenkins_home``` folder
* ```/cd3user/tenancies/jenkins_home/jobs/<prefix>``` folder 
* ```/cd3user/tenancies/<prefix>``` folder

<br>

<span style="color: teal;"><b>Step 4 - Restart Jenkins:</b></span>

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
