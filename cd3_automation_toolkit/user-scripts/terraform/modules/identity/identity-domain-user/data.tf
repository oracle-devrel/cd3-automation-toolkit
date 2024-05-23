// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Data Block - Identity
# Create Users
#############################

data "oci_identity_domains" "iam_domains" {
  # Required
  compartment_id = var.tenancy_ocid

  # Optional
  display_name = var.idcs_endpoint

}


#data "oci_identity_groups" "iam_groups" {
  #Required
  #compartment_id = var.tenancy_ocid

  #Optional
  #name = var.group_name
#}
