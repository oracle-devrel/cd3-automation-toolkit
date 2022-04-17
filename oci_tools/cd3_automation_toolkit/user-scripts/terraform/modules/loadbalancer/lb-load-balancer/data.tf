locals {
  nsg_ids = flatten(tolist([for nsg in var.network_security_group_ids : (length(regexall("ocid1.networksecuritygroup.oc1*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)]))
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each       = { for nsg in var.network_security_group_ids : nsg => nsg }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_lbs[var.vcn_names[0]].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_lbs" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}

data "oci_core_subnets" "oci_subnets_lbs" {
  for_each       = { for subnet in var.subnet_ids : subnet => subnet }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_lbs[var.vcn_names[0]].virtual_networks.*.id[0]
}
