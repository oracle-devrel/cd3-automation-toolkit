# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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