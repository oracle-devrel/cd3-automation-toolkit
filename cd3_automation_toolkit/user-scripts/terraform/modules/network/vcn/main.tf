# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create VCNs
############################

resource "oci_core_vcn" "vcn" {

  #Required
  compartment_id = var.compartment_id

  #Optional
  dynamic "byoipv6cidr_details" {
    for_each = try(var.byoipv6cidr_details != [] ? var.byoipv6cidr_details : [], [])
    content {
      #Required
      byoipv6range_id = byoipv6cidr_details.value.byoipv6range_id
      ipv6cidr_block  = byoipv6cidr_details.value.ipv6cidr_block
    }
  }
  #Optional
  cidr_blocks                      = var.cidr_blocks
  defined_tags                     = var.defined_tags
  display_name                     = var.display_name
  dns_label                        = var.dns_label
  freeform_tags                    = var.freeform_tags
  is_ipv6enabled                   = var.is_ipv6enabled
  ipv6private_cidr_blocks          = var.ipv6private_cidr_blocks
  is_oracle_gua_allocation_enabled = var.is_oracle_gua_allocation_enabled
  lifecycle {
    create_before_destroy = true
  }
}