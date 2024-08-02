# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Governance
# Create Namespaces
############################

resource "oci_identity_tag_namespace" "tag_namespace" {
  #Required
  compartment_id = var.compartment_id != null ? var.compartment_id : var.tenancy_ocid
  description    = var.description
  name           = var.name

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  is_retired    = var.is_retired
}