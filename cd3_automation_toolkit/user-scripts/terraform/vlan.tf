# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Network - VLAN
# Create VLAN
############################################

data "oci_core_route_tables" "oci_route_tables_vlans" {
  # depends_on     = [module.route-tables]  #Uncomment this if using single outdir for Network and VLANs
  for_each       = var.vlans != null ? var.vlans : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.route_table_name
  vcn_id         = data.oci_core_vcns.oci_vcns_vlans[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_vlans" {
  for_each       = var.vlans != null ? var.vlans : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  display_name   = each.value.vcn_name
}

module "vlans" {
  source   = "./modules/network/vlan"
  for_each = var.vlans != null ? var.vlans : {}

  compartment_id         = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  cidr_block             = each.value.cidr_block != "" ? each.value.cidr_block : null
  vcn_id                 = flatten(data.oci_core_vcns.oci_vcns_vlans[each.key].virtual_networks.*.id)[0]
  display_name           = each.value.display_name != "" ? each.value.display_name : null
  nsg_ids                = each.value.nsg_ids
  route_table_id         = each.value.route_table_name != null ? (length(regexall("ocid1.routeteable.oc*", each.value.route_table_name)) > 0 ? each.value.route_table_name : data.oci_core_route_tables.oci_route_tables_vlans[each.key].route_tables.*.id[0]) : null
  #route_table_id    = each.value.route_table_name != null ? (length(regexall("ocid1.routeteable.oc*", each.value.route_table_name)) > 0 ? each.value.route_table_name : try(data.oci_core_route_tables.oci_route_tables_vlans[each.key].route_tables.*.id[0], module.route-tables["${each.value.vcn_name}_${each.value.route_table_name}"]["route_table_ids"])): null
  vlan_tag            = each.value.vlan_tag != "" ? each.value.vlan_tag : null
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  defined_tags        = each.value.defined_tags
  freeform_tags       = each.value.freeform_tags
}


