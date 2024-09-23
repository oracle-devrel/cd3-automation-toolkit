# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Public IP Pool
## Create Public IP Pool
################################

resource "oci_core_public_ip_pool" "public_ip_pool" {
  #Required
  compartment_id = var.compartment_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags
}