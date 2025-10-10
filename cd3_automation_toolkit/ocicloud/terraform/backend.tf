# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
/*This line will be removed when using remote state
# !!! WARNING !!! Terraform State Lock is not supported with OCI Object Storage.
# Pre-Requisite: Create a version enabled object storage bucket to store the state file.
# End Point Format: https://<namespace>.compat.objectstorage.<region>.oraclecloud.com
# Please look at the below doc for information about shared_credentials_file and other parameters:
# Reference: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/terraformUsingObjectStore.htm

terraform {
  backend "s3" {
    key      = "<folder/filename.tfstate>"
    bucket   = "<Object Storage Bucket Name>"
    region   = "<region>"
    endpoint = "<Object Storage Bucket End Point>"
    shared_credentials_file     = "~/.aws/credentials"
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    force_path_style            = true
  }
}
This line will be removed when using remote state*/