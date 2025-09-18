# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create DRG Route Distribution
############################

resource "oci_core_drg_route_distribution" "drg_route_distribution" {

  #Required
  distribution_type = var.distribution_type
  drg_id            = var.drg_id

  #Optional
  defined_tags  = var.defined_tags == {} ? null : var.defined_tags
  freeform_tags = var.freeform_tags == {} ? null : var.freeform_tags
  display_name  = var.display_name == "" ? null : var.display_name

}