# Store Terraform State into Object Storage Bucket

* Toolkit provides the option to store terraform state file(tfstate) into Object Storage bucket.
* This can be achieved by setting ```use_remote_state=yes``` under Advanced Parameters in ```tenancyConfig.properties``` file while executing ```createTenancyConfig.py```.
* Setting above parameter will create a versioning enabled bucket in OCI tenancy (if you don't specify anything in ```remote_state_bucket_name``` parameter to use an existing bucket)

