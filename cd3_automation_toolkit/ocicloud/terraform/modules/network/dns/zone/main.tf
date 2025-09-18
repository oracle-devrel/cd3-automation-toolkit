# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
########################
# Resource Block - DNS #
########################

resource "oci_dns_zone" "zone" {
  #Required
  compartment_id = var.zone_compartment_id
  name           = var.zone_name
  zone_type      = var.zone_type

  #Optional
  defined_tags = var.zone_defined_tags
  #dynamic "external_masters" {   # dynamic when zone_type is SECONDARY
  #    for_each = var.zone_type == "SECONDARY" ? (var.external_masters != null ? var.external_masters : {}) : {}
  #	content {
  #    #Required
  #    address = external_masters.value.address
  #
  #    #Optional
  #    port = external_masters.value.port != null ? external_masters.value.port : null
  #    tsig_key_id = external_masters.value.tsig_key_id != null ? external_masters.value.tsig_key_id : null
  #	}
  #}
  freeform_tags = var.zone_freeform_tags
  scope         = var.zone_scope != null ? (var.zone_scope == "PRIVATE" ? var.zone_scope : null) : null # PRIVATE to create PRIVATE zone otherwise null
  view_id       = var.view_id
}