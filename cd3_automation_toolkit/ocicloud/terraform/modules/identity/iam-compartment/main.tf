# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Identity
# Create Compartments
############################

resource "oci_identity_compartment" "compartment" {

  #Required
  compartment_id = var.compartment_id != null ? var.compartment_id : var.tenancy_ocid
  description    = var.compartment_description
  name           = var.compartment_name

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  enable_delete = var.enable_delete

}
