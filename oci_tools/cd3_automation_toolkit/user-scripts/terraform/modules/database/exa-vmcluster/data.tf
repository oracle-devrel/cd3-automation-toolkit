locals {
  nsg_ids = flatten(tolist([for nsg in var.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)]))

  backup_nsg_ids = flatten(tolist([for nsg in var.backup_network_nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.backup_network_security_groups[nsg].network_security_groups[*].id)]))
 
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each = {for nsg in var.nsg_ids: nsg => nsg }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
 # vcn_id = "<<VCN_ID_HERE>>"
}

data "oci_core_network_security_groups" "backup_network_security_groups" {
  for_each = {for nsg in var.backup_network_nsg_ids: nsg => nsg }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
 # vcn_id = "<<VCN_ID_HERE>>"
}


