# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Resource Block - Identity
# Create Policies 
#############################

resource "oci_identity_policy" "policy" {

  # Required
  compartment_id = var.policy_compartment_id
  description    = var.policy_description
  name           = var.policy_name
  statements     = var.policy_statements

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  version_date  = var.policy_version_date

}
