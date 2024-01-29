# Migrate Jobs from Automation Toolkit Jenkins to Customer Jenkins Environment


1. Copy Jobs Folder
    - Copy the folders from the Automation Toolkit Jenkins home path `/cd3user/tenancies/jenkins_home/jobs/` to the corresponding home directory in the Customer Jenkins instance (typically `/var/jenkins_home`).
      
      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/5a1f54f1-3e50-4ec7-8634-494eec65ce56)

2. Set up Repository SSH Authentication
    - Ensure SSH authentication is configured and operational on the Customer Jenkins instance. For detailed instructions, refer to the [OCI Code Repository documentation](https://docs.oracle.com/en-us/iaas/Content/devops/using/ssh_auth.htm).
    
3. Ensure Availability of Ansi Color Plugin
    - Confirm the presence of the Ansi color plugin in the Customer Jenkins instance. This plugin is utilized in Automation Toolkit pipeline Groovy code and is necessary if not already installed. Plugin link: [Ansicolor Plugin](https://plugins.jenkins.io/ansicolor/)

4. Install Terraform Binary
    - Make sure the Terraform binary is installed and accessible for the Jenkins user within the Jenkins instance. Installation guide: [Terraform Installation](https://developer.hashicorp.com/terraform/install)

5. Update Optional Attribute Field inside Terraform Provider Block
    - Include an optional attribute field within the Terraform provider block. This is optional but necessary in case Terraform plan encounters an error.
      
      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/2e1593ee-e4cc-4439-8ffa-97d39dda16a6)

6. Update the Correct Key Path in Global Variables_<Region> File inside outdir
    - It varies and depends on user selection during tenancy setup. i.e. single outdir or multi outdir.
      
      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/d673bb87-0124-44eb-a75c-1d420edc7841)

7. Configure S3 Backend Credentials in Customer Jenkins Instance
    - Update the correct path within the `backend.tf` file for Terraform.

      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/bfd6d2a2-7384-4bb0-a30b-5b7fd63c0e9b)

8. Job and Pipeline Configuration
    - Verify that the specified jobs and pipelines, initialized by the Automation Toolkit, are visible in the Customer Jenkins instance.
      
      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/3fca2b65-78b0-4528-a821-c43b5950cc90)


9. Pipeline Job Output
    
      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/4bb57802-1594-4361-9c54-46022abf190a)


# Update the Git URL for all pipeline jobs in the Customer Jenkins(if required).

1. Create `jenkins.properties` File
    - Copy the `jenkins.properties` file from Automation Toolkit Jenkins home folder `/cd3users/tenancies/jenkins_home/` to the `/var/jenkins_home/` directory in customer Jenkins Instance (Below is sample content):

          git_url= "ssh://devops.scmservice.us-phoenix-1.oci.oraclecloud.com/namespaces/<namespace>/projects/toolkitdemo-automation-toolkit-project/repositories/toolkitdemo-automation-toolkit-repo"
          regions=['london', 'phoenix']
          services=['identity', 'tagging', 'network', 'loadbalancer', 'vlan', 'nsg', 'compute', 'database', 'fss', 'oke', 'ocvs', 'security', 'managementservices', 'budget', 'cis', 'oss', 'dns']
          outdir_structure=["Multiple_Outdir"]
      

2. Update the `git_url` in the `jenkins.properties` File
    - Open the `jenkins.properties` file located in the `/var/jenkins_home/` directory.
    - Update the `git_url` in the file with the new Git server URL.
      
      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/2056b8a3-c27e-481a-893a-a2ffba628c03)


3. Copy `01_jenkins-config.groovy` File
    - Copy the `01_jenkins-config.groovy` file from the Automation Toolkit Jenkins path (`/cd3user/tenancies/jenkins_home/init.groovy.d`) to the init path of the Customer Jenkins instance.
    - Update the path to the groovy file accordingly.

      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/348db348-7eee-47ed-88f4-32f1ecd25e0b)


4. Restart Customer Jenkins Instance
    - Stop and start the Customer Jenkins instance to apply the changes.
    - After that, all Git URLs will be updated and point to new Git Url inside pipeline jobs.

      ![image](https://github.com/unamachi/cd3-automation-toolkit/assets/103548537/83dc5e7a-4ceb-44a1-871f-4d9e314a3ce1)

5. Ensure SSH Authentication
    - Confirm that SSH authentication is enabled for the new GIT repository from the Jenkins instance.
    - Alternatively, use the respective authentication method if relying on other methods.
