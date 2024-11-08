# Migrate Jobs from Automation Toolkit Jenkins to Customer Jenkins Environment


1. Copy Jobs Folder
    - Copy the folders from the Automation Toolkit Jenkins home path `/cd3user/tenancies/jenkins_home/jobs/` to the corresponding home directory in the Customer Jenkins instance (typically `/var/jenkins_home`).
      
        ![image](../images/migratejobs-1.png)

2. Set up OCI Devops repository SSH Authentication
    - Ensure SSH authentication is configured and operational on the Customer Jenkins instance. For detailed instructions, refer to the <a href="https://docs.oracle.com/en-us/iaas/Content/devops/using/ssh_auth.htm"><u>OCI Code Repository documentation</u></a>.<br>
  
        > Note - Steps to change the GIT repo are explained in next section.

    - Ensure the Git repository has all the generated terraform code and branches for the terraform deployment pipelines to work properly for customer prefixes. 
    
        Copy or create the SSH configuration file from the CD3 Jenkins instance to the customer's Jenkins instance. The file is located at /cd3user/.ssh/config on the CD3 Jenkins instance.

    
3. Ensure Availability of Ansi Color Plugin
    - Confirm the presence of the Ansi color plugin in the Customer Jenkins instance. This plugin is utilized in Automation Toolkit pipeline Groovy code and is necessary if not already installed. Plugin link: <a href="https://plugins.jenkins.io/ansicolor/"><u>Ansicolor Plugin</u></a>.

4. Install Terraform Binary
    - Make sure the Terraform binary is installed and accessible for the Jenkins user within the Jenkins instance. Installation guide: <a href="https://developer.hashicorp.com/terraform/install"><u>Terraform Installation</u></a>.

5. Update Optional Attribute Field inside Terraform Provider Block at `/cd3user/tenancies/<prefix>/terraform_files/<region><service_dir>/provider.tf`
    - Include an  attribute as highlighted below within the Terraform provider block. This is optional but necessary in case Terraform plan encounters an error.
  
              experiments = [module_variable_optional_attrs]
      
        ![image](../images/migratejobs-2.png)

6. Update the correct value for private_key_path variable in `/cd3user/tenancies/<prefix>/terraform_files/<region><service_dir>/variables_<region>.tf`

7. Configure S3 Backend Credentials in Customer Jenkins Instance
    - Update the correct path within the `backend.tf` file for Terraform.

        ![image](../images/migratejobs-3.png)

8. Push the above changes to Devops GIT repository so that pipline can get the latest commits/changes and execute it.

9. Stop/Start the Customer Jenkins Instance for the changes to take effect. This is applicable for any configuration changes in Jenkins.

    Additionally, copy the init.groovy.d folder from the jenkins_home directory of the CD3 Jenkins instance to the jenkins_home directory of the customer's instance

10. Job and Pipeline Configuration
    - Verify that the specified jobs and pipelines, initialized by the Automation Toolkit, are visible in the Customer Jenkins instance.
      
        ![image](../images/migratejobs-4.png)

11. Pipeline Job Output
        ![image](../images/migratejobs-5.png)

<br>
# Update the Git URL for all pipeline jobs in the Customer Jenkins(if required).

1. Remove terraform_files folder under <customer_jenkins_home>/jobs folder
2. Create `jenkins.properties` File
    - Copy the `jenkins.properties` file from Automation Toolkit Jenkins home folder `/cd3users/tenancies/jenkins_home/` to the customer jenkins home (typically `/var/jenkins_home/`) directory in customer Jenkins Instance (Below is sample content):

          git_url= "ssh://devops.scmservice.us-phoenix-1.oci.oraclecloud.com/namespaces/<namespace>/projects/toolkitdemo-automation-toolkit-project/repositories/toolkitdemo-automation-toolkit-repo"
          regions=['london', 'phoenix']
          services=['identity', 'tagging', 'network', 'loadbalancer', 'vlan', 'nsg', 'compute', 'database', 'fss', 'oke', 'ocvs', 'security', 'managementservices', 'budget', 'cis', 'oss', 'dns']
          outdir_structure=["Multiple_Outdir"]
      

3. Update the `git_url` in the `jenkins.properties` File
    - Open the `jenkins.properties` file located in the `/var/jenkins_home/` directory.
    - Update the `git_url` in the file with the new Git server URL.
      
        ![image](../images/migratejobs-6.png)


4. Copy `01_jenkins-config.groovy` File
    - Copy the `01_jenkins-config.groovy` file from the Automation Toolkit Jenkins path (`/cd3user/tenancies/jenkins_home/init.groovy.d`) to the init path of the Customer Jenkins instance.
    - Update the path to the groovy file accordingly.

         <img height=1500 width=700 src="../images/migratejobs-7.png">


5. Restart Customer Jenkins Instance
    - Stop and start the Customer Jenkins instance to apply the changes.
    - After that, all Git URLs will be updated and point to new Git Url inside pipeline jobs.

        ![image](../images/migratejobs-8.png)

6. Ensure SSH Authentication
    - Confirm that SSH authentication is enabled for the new GIT repository from the Jenkins instance.
    - Alternatively, use the respective authentication method if relying on other methods.
