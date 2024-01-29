# Store Terraform State into Object Storage Bucket

> [!Caution]  
> If you are using remote state and upload the stack to OCI Resource Manager using <b>Upload current terraform files/state to Resource Manager</b> under <b>Developer Services</b>, then running terraform plan/apply from OCI Resource Manager will not work and shows below error:
> 
<img width="597" alt="Screenshot 2024-01-17 at 11 38 54 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/1b0cd9fa-1ac0-42c4-9c33-14ad4bf0ddb8">

> You will have to remove backend.tf from the directory, bring the remote state into local and then re-upload the stack.

<br><br>
* Toolkit provides the option to store terraform state file(tfstate) into Object Storage bucket.
* This can be achieved by setting ```use_remote_state=yes``` under Advanced Parameters in ```tenancyconfig.properties``` file while executing ```createTenancyConfig.py```.
* Setting above parameter will -
    - create a versioning enabled bucket in OCI tenancy in the specified region(if you don't specify anything in ```remote_state_bucket_name``` parameter to use an existing bucket)
    - create a customer secret key for the user(specified in DevOps User Details or user ocid) and configure that as S3 credentials to accesss the bucket. There is a limit of max 2 customer secret keys for any user. So make sure that user does not already have 2 secret keys assigned before running createTenancyConfig.py.
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
