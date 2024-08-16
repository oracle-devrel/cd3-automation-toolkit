# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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