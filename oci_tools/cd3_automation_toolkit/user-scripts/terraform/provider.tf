// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Provider Block 
# OCI
############################

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

terraform {
  required_providers {
    oci = {
      #source  = "oracle/oci"
      version = ">= 3.0.0"
    }
  }
  required_version = ">= 1.0.0"
}

/*
# Uncomment and update to use Object Storage Bucket as the backend
# !!! WARNING !!! Terraform State Lock is not supported in this approach; use Oracle Resource Manager for the same
# Reference: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/terraformUsingObjectStore.htm
terraform {
  backend "s3" {
    bucket   = "<Object Storage Bucket Name>"
    key      = "<folder/filename.tfstate>"
    region   = "<region>"
    endpoint = "<Object Storage Bucket End Point>"
    shared_credentials_file     = "~/.aws/credentials"
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    force_path_style            = true
  }
}
*/