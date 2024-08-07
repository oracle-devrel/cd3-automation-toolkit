// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Data Block - Identity
# Create Groups
#############################
/*
data "oci_identity_domains" "iam_domains" {
  # Required
  compartment_id = var.compartment_id
  # Optional
  display_name = var.idcs_endpoint

}*/

############################
# Data Source Block - Identity
# Get User Information by Email
############################


data "oci_identity_domains_users" "users" {
  idcs_endpoint = var.identity_domain.url
}






