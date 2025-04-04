# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
      source  = "oracle/oci"
      version = "6.30.0"
    }
  }
}
