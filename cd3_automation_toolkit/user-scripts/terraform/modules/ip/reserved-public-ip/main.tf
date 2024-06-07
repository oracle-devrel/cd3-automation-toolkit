// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Resource Block - Reserved IP
## Create Reserved IP
################################

resource "oci_core_public_ip" "public_ip" {
  #Required
  compartment_id = var.compartment_id
  lifetime       = var.lifetime

  #Optional
  defined_tags      = var.defined_tags
  display_name      = var.display_name
  freeform_tags     = var.freeform_tags
  private_ip_id     = var.private_ip_id
  public_ip_pool_id = var.public_ip_pool_id

}