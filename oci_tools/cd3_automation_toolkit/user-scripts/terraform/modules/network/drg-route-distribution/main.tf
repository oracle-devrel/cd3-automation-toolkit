// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}