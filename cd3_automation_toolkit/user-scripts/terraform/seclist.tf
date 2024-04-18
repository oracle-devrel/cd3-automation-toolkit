############################
# Module Block - Network
# Create Default Security Lists
############################

module "default-security-lists" {
  source   = "./modules/network/default-sec-list"
  for_each = (var.default_seclists != null || var.default_seclists != {}) ? var.default_seclists : {}

  #Required
  manage_default_resource_id = length(regexall("ocid1.vcn.oc1*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_security_list_id"]

  key_name        = each.key
  defined_tags    = each.value.defined_tags
  display_name    = each.value.display_name != null ? each.value.display_name : null
  freeform_tags   = each.value.freeform_tags
  seclist_details = var.default_seclists
}

/*
output "default_seclist_id_map" {
  value = [ for k,v in merge(module.default-security-lists.*...) : v.default_seclist_id ]
}
*/


############################
# Module Block - Network
# Create Custom Security Lists
############################

data "oci_core_vcns" "oci_vcns_sec_lists" {
  # depends_on = [module.vcns] # Uncomment to create Network and NSGs together
  for_each       = var.nsgs != null ? var.nsgs : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  display_name   = each.value.vcn_name
}


module "security-lists" {
  source   = "./modules/network/sec-list"
  for_each = (var.seclists != null || var.seclists != {}) ? var.seclists : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  vcn_id = length(regexall("ocid1.vcn.oc1*", each.value.vcn_id)) > 0 ? each.value.vcn_id : flatten(data.oci_core_vcns.oci_vcns_sec_lists[each.key].virtual_networks.*.id)[0]

  key_name        = each.key
  defined_tags    = each.value.defined_tags
  display_name    = each.value.display_name != null ? each.value.display_name : null
  freeform_tags   = each.value.freeform_tags
  seclist_details = var.seclists
}

/*
output "seclist_id_map" {
  value = [ for k,v in merge(module.security-lists.*...) : v.seclist_id ]
}
*/
