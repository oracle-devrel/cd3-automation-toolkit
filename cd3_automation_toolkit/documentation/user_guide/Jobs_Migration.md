# Migrate Jobs from Automation Toolkit Jenkins to Customer Jenkins Environment


## 1. Copy Jobs Folder
- Copy the folders from the Automation Toolkit Jenkins home path `/cd3user/tenancies/jenkins_home/jobs/` to the corresponding home directory in the Customer Jenkins instance (typically `/var/jenkins_home`).

## 2. Set up Repository SSH Authentication
- Ensure SSH authentication is configured and operational on the Customer Jenkins instance. For detailed instructions, refer to the [OCI Code Repository documentation](https://docs.oracle.com/en-us/iaas/Content/devops/using/ssh_auth.htm).

## 3. Ensure Availability of Ansi Color Plugin
- Confirm the presence of the Ansi color plugin in the Customer Jenkins instance. This plugin is utilized in Automation Toolkit pipeline Groovy code and is necessary if not already installed. Plugin link: [Ansicolor Plugin](https://plugins.jenkins.io/ansicolor/)

## 4. Install Terraform Binary
- Make sure the Terraform binary is installed and accessible for the Jenkins user within the Jenkins instance. Installation guide: [Terraform Installation](https://developer.hashicorp.com/terraform/install)

## 5. Update Optional Attribute Field inside Terraform Provider Block
- Include an optional attribute field within the Terraform provider block. This is optional but necessary in case Terraform plan encounters an error.

## 6. Update the Correct Key Path in Global Variables_<Region> File inside outdir
- It varies and depends on user selection during tenancy setup. i.e. single outdir or multi outdir.

## 7. Configure S3 Backend Credentials in Customer Jenkins Instance
- Update the correct path within the `backend.tf` file for Terraform.

## 8. Job and Pipeline Configuration
- Verify that the specified jobs and pipelines, initialized by the Automation Toolkit, are visible in the Customer Jenkins instance.

## 9. Pipeline Job


# Update the Git URL for all pipeline jobs in the Customer Jenkins(if required).

## 1. Create `jenkins.properties` File
- Copy the `jenkins.properties` file from Automation Toolkit Jenkins home folder `/cd3users/tenancies/jenkins_home/` to the `/var/jenkins_home/` directory in customer Jenkins Instance (Below is sample content):
  ```properties
  git_url= "ssh://devops.scmservice.us-phoenix-1.oci.oraclecloud.com/namespaces/<namespace>/projects/toolkitdemo-automation-toolkit-project/repositories/toolkitdemo-automation-toolkit-repo"
  regions=['london', 'phoenix']
  services=['identity', 'tagging', 'network', 'loadbalancer', 'vlan', 'nsg', 'compute', 'database', 'fss', 'oke', 'ocvs', 'security', 'managementservices', 'budget', 'cis', 'oss', 'dns']
  outdir_structure=["Multiple_Outdir"]


## 2. Update the `git_url` in the `jenkins.properties` File
- Open the `jenkins.properties` file located in the `/var/jenkins_home/` directory.
- Update the `git_url` in the file with the new Git server URL.

## 3. Copy `01_jenkins-config.groovy` File
- Copy the `01_jenkins-config.groovy` file from the Automation Toolkit Jenkins path (`/cd3user/tenancies/jenkins_home/init.groovy.d`) to the init path of the Customer Jenkins instance.
- Update the path to the groovy file accordingly.

## 4. Restart Customer Jenkins Instance
- Restart the Customer Jenkins instance to apply the changes.
- After the restart, all Git URLs will be updated and point to new Git Url.

## 5. Ensure SSH Authentication
- Confirm that SSH authentication is enabled for the new GIT repository from the Jenkins instance.
- Alternatively, use the respective authentication method if relying on alternatives.
