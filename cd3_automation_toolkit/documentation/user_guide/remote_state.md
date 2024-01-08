# Store Terraform State into Object Storage Bucket

* Toolkit provides the option to store terraform state file(tfstate) into Object Storage bucket.
* This can be achieved by setting ```use_remote_state=yes``` under Advanced Parameters in ```tenancyConfig.properties``` file while executing ```createTenancyConfig.py```.
* Setting above parameter will -
    - create a versioning enabled bucket in OCI tenancy (if you don't specify anything in ```remote_state_bucket_name``` parameter to use an existing bucket)
    - create Customer Secret Key for the user(specified in DevOps User Details or user ocid) and configure that as S3 credentials to accesss the bucket. There is a limit of max 2 customer secret keys for any user. So make sure that user does not already have 2 secret keys assigned before running createTenanceConfig.py.

