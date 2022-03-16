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
      version = ">= 3.0.0"
    }
  }
  required_version = ">= 1.0.0"
}