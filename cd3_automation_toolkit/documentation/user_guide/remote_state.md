# Store Terraform State into Object Storage Bucket

* Toolkit provides the option to store terraform state file(tfstate) into Object Storage bucket.
* This can be achieved by setting ```use_remote_state=yes``` under Advanced Parameters in ```tenancyConfig.properties``` file while executing ```createTenancyConfig.py```.
* Setting above parameter will -
    - create a versioning enabled bucket in OCI tenancy in the specified region(if you don't specify anything in ```remote_state_bucket_name``` parameter to use an existing bucket)
    - create a customer secret key for the user(specified in DevOps User Details or user ocid) and configure that as S3 credentials to accesss the bucket. There is a limit of max 2 customer secret keys for any user. So make sure that user does not already have 2 secret keys assigned before running createTenanceConfig.py.
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

* For single outdir, tfstate for all subscribed regions will be stored as ```<region>\tfstate``` eg ```london\terraform.tfstate``` for london ```phoenix\terraform.tfstate``` for phoenix.


