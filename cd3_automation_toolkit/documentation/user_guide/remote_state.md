# Store Terraform State into Object Storage Bucket

> [!Caution]  
> When utilizing remote state and deploying the stack to OCI Resource Manager through the **Upload current terraform files/state to Resource Manager** option under **Developer Services**, attempting to execute terraform plan/apply directly from OCI Resource Manager may result in below error.
> 
<img width="597" alt="Screenshot 2024-01-17 at 11 38 54 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/1b0cd9fa-1ac0-42c4-9c33-14ad4bf0ddb8">

> This option is disabled while using the toolkit via Jenkins. While using it via CLI, you will have to remove backend.tf from the directory, bring the remote state into local and then upload the stack.

<br><br>
* Toolkit provides the option to store terraform state file(tfstate) into Object Storage bucket.
* This can be achieved by setting ```use_remote_state=yes``` under Advanced Parameters in ```tenancyconfig.properties``` file while executing ```createTenancyConfig.py```.
* Upon setting above parameter the script will -
    - create a versioning enabled bucket in OCI tenancy in the specified region(if you don't specify anything in ```remote_state_bucket_name``` parameter to use an existing bucket)
    - create a new customer secret key for the user, and configure it as S3 credentials to access the bucket. Before executing the createTenancyConfig.py script, ensure that the specified user in the DevOps User Details or identified by the user OCID does not already have the maximum limit of two customer secret keys assigned. 
      
* backend.tf file that gets generated -
  
  ```
  terraform {
  backend "s3" {
    key      = "<region_name>/<service_dir_name>/terraform.tfstate"
    bucket   = "<customer_name>-automation-toolkit-bucket"
    region   = "<region>"
    endpoint = "https://<namespace>.compat.objectstorage.<region>.oraclecloud.com"
    shared_credentials_file     = "/cd3user/tenancies/<customer_name>/.config_files/<customer_name>_s3_credentials"
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    force_path_style            = true
    }
  }  
  ```

* For single outdir, tfstate for all subscribed regions will be stored as ```<region>\terraform.tfstate``` eg ```london\terraform.tfstate``` for london ```phoenix\terraform.tfstate``` for phoenix.
* For multi outdir, tfstate for all services in all subscribed regions will be stored as ```<region>\<service_dir_name>\terraform.tfstate``` eg ```london\tagging\terraform.tfstate``` for tagging dir in london region

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/cli_jenkins.md">:arrow_backward: Prev</a> |
| :---- | 
  
</div>
