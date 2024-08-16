# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Module Block - Network
# Create Network Security Groups
#############################

data "oci_core_vcns" "oci_vcns_nsgs" {
  # depends_on = [module.vcns] # Uncomment to create Network and NSGs together
  for_each       = var.nsgs != null ? var.nsgs : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  display_name   = each.value.vcn_name
}



module "nsgs" {
  source   = "./modules/network/nsg"
  for_each = (var.nsgs != null || var.nsgs != {}) ? var.nsgs : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = flatten(data.oci_core_vcns.oci_vcns_nsgs[each.key].virtual_networks.*.id)[0]
  defined_tags   = each.value.defined_tags
  display_name   = each.value.display_name
  freeform_tags  = each.value.freeform_tags
}

/*
output "nsg_id_map" {
	value = [ for k,v in merge(module.nsgs.*...) : v.nsg_tf_id ]
}
*/

module "nsg-rules" {
  source     = "./modules/network/nsg-rule"
  for_each   = (var.nsg_rules != null || var.nsg_rules != {}) ? var.nsg_rules : {}
  depends_on = [module.nsgs]

  #Required
  nsg_id    = length(regexall("ocid1.networksecuritygroup.oc*", each.value.nsg_id)) > 0 ? each.value.nsg_id : merge(module.nsgs.*...)[each.value.nsg_id]["nsg_tf_id"]
  direction = (each.value.direction == "" && each.value.direction == null) ? "INGRESS" : each.value.direction
  protocol  = each.value.protocol

  #Optional
  description       = each.value.description
  destination_addr  = (each.value.destination_type == "NETWORK_SECURITY_GROUP") ? merge(module.nsgs.*...)[each.value.destination]["nsg_tf_id"] : each.value.destination
  destination_type  = each.value.destination_type
  source_addr       = each.value.source_type == "NETWORK_SECURITY_GROUP" ? merge(module.nsgs.*...)[each.value.source]["nsg_tf_id"] : each.value.source
  source_type       = each.value.source_type
  stateless         = (each.value.stateless != "" && each.value.stateless != null) ? each.value.stateless : false
  key_name          = each.key
  nsg_rules_details = var.nsg_rules
}
