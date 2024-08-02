# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Governance
# Create Tag Defaults
############################

resource "oci_identity_tag_default" "tag_default" {
  #Required
  compartment_id    = var.compartment_id
  tag_definition_id = var.tag_definition_id
  value             = var.value

  #Optional
  is_required = var.is_required
}