// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Provider Block 
# OCI
############################

provider "oci" {
  tenancy_ocid        = var.tenancy_ocid
  user_ocid           = var.user_ocid
  fingerprint         = var.fingerprint
  private_key_path    = var.private_key_path
  region              = var.region
  ignore_defined_tags = ["Oracle-Tags.CreatedBy", "Oracle-Tags.CreatedOn"]
}

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
      version = "5.40.0"
    }
  }
}
