# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##############################################
# Resource Block - DNS resolver and Endpoint #
##############################################

resource "oci_dns_resolver" "resolver" {
  #Required
  resolver_id = var.target_resolver_id

  #Optional
  dynamic "attached_views" {
    for_each = var.views != null ? var.views : null
    #Required
    content {
      view_id = attached_views.value.view_id
    }

  }
  defined_tags  = var.resolver_defined_tags
  freeform_tags = var.resolver_freeform_tags
  display_name  = var.resolver_display_name != null ? var.resolver_display_name : null

  dynamic "rules" {
    for_each = var.resolver_rules
    content {
      #Required
      action                = "FORWARD"
      destination_addresses = rules.value.destination_addresses
      source_endpoint_name  = oci_dns_resolver_endpoint.resolver_endpoint[rules.value.source_endpoint_name].name

      #Optional
      client_address_conditions = rules.value.client_address_conditions
      #		!= null ? rules.value.client_address_conditions : null
      qname_cover_conditions = rules.value.qname_cover_conditions
      #!= null ? rules.value.qname_cover_conditions : null
    }
  }
}

resource "oci_dns_resolver_endpoint" "resolver_endpoint" {
  #Required
  for_each      = var.endpoint_names
  is_forwarding = each.value.forwarding != null ? (each.value.listening == false ? each.value.forwarding : false) : false
  is_listening  = each.value.listening != null ? (each.value.forwarding == false ? each.value.listening : false) : false
  name          = each.key
  resolver_id   = var.target_resolver_id
  subnet_id     = each.value.subnet_id
  #Optional
  endpoint_type      = each.value.endpoint_type # "VNIC"
  forwarding_address = each.value.forwarding_address != null ? (each.value.forwarding == true ? each.value.forwarding_address : null) : null
  listening_address  = each.value.listening_address != null ? (each.value.listening == true ? each.value.listening_address : null) : null
  nsg_ids            = each.value.nsg_ids != null ? [for ids in each.value.nsg_ids : ids] : null
  #lifecycle {
  #create_before_destroy = true
  #}
}