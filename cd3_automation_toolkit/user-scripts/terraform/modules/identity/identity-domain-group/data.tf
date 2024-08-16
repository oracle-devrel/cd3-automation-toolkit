# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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






