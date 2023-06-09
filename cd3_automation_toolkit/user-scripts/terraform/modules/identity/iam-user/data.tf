// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Data Block - Identity
# Create Users
#############################


data "oci_identity_groups" "iam_groups" {
  #Required
  compartment_id = var.tenancy_ocid

  #Optional
  name = var.group_name
}