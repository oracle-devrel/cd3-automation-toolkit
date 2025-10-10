# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create DRG Route Table
############################


resource "oci_core_drg_route_table" "drg_route_table" {

  #Required
  drg_id = var.drg_id

  #Optional
  defined_tags                     = var.defined_tags
  display_name                     = var.display_name
  freeform_tags                    = var.freeform_tags
  import_drg_route_distribution_id = var.import_drg_route_distribution_id
  is_ecmp_enabled                  = var.is_ecmp_enabled
}