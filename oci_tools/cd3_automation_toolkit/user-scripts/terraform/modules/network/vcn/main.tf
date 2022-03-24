// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create VCNs
############################

resource "oci_core_vcn" "vcn" {

  #Required
  compartment_id = var.compartment_id

  #Optional
  cidr_blocks    = var.cidr_blocks
  defined_tags   = var.defined_tags
  display_name   = var.display_name
  dns_label      = var.dns_label
  freeform_tags  = var.freeform_tags
  is_ipv6enabled = var.is_ipv6enabled

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}