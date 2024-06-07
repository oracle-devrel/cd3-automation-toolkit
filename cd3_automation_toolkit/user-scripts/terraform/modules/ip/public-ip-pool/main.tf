// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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