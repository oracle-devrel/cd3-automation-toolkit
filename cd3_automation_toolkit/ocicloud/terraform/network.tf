# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
# Data Block - Network
# DRG Route Rules and DRG Route Distributions
################################

locals {
  all_route_tables  = merge(var.route_tables, var.default_route_tables)
  all_seclists      = merge(var.seclists, var.default_seclists)
  gateway_rt_status = { for k, v in local.all_route_tables : k => (v.gateway_route_table == null ? false : v.gateway_route_table) }
}


data "oci_core_drg_route_tables" "drg_route_tables" {
  for_each = (var.data_drg_route_tables != null || var.data_drg_route_tables != {}) ? var.data_drg_route_tables : {}

  #Required
  drg_id = length(regexall("ocid1.drg.oc*", each.value.drg_id)) > 0 ? each.value.drg_id : merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"]
  filter {
    name   = "display_name"
    values = [each.value.values]
  }

}


data "oci_core_drg_route_distributions" "drg_route_distributions" {
  for_each = (var.data_drg_route_table_distributions != null || var.data_drg_route_table_distributions != {}) ? var.data_drg_route_table_distributions : {}

  #Required
  drg_id = length(regexall("ocid1.drg.oc*", each.value.drg_id)) > 0 ? each.value.drg_id : merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"]
  filter {
    name   = "display_name"
    values = [each.value.values]
  }

}

############################
# Module Block - Network
# Create VCNs
############################

module "vcns" {
  source   = "./modules/network/vcn"
  for_each = var.vcns != null ? var.vcns : {}

  #Required
  #compartment_id = length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : try(zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.compartment_id], var.compartment_ocids[each.value.compartment_id])
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  cidr_blocks                      = each.value.cidr_blocks
  display_name                     = each.value.display_name
  byoipv6cidr_details              = each.value.byoipv6cidr_details != null ? each.value.byoipv6cidr_details : []
  dns_label                        = (each.value.dns_label == "n") ? null : each.value.dns_label
  is_ipv6enabled                   = each.value.is_ipv6enabled # Defaults to false by terraform hashicorp
  defined_tags                     = each.value.defined_tags
  freeform_tags                    = each.value.freeform_tags
  ipv6private_cidr_blocks          = each.value.ipv6private_cidr_blocks
  is_oracle_gua_allocation_enabled = each.value.is_oracle_gua_allocation_enabled

}

/*
output "vcn_id_map" {
  value = [ for k,v in merge(module.vcns.*...) : v.vcn_id ]
}
*/

############################
# Module Block - Network
# Create Internet Gateways
############################

module "igws" {
  source   = "./modules/network/igw"
  for_each = (var.igws != null || var.igws != {}) ? var.igws : {}

  depends_on = [module.vcns] #,module.route-tables]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  enabled        = each.value.enable_igw # Defaults to true by terraform hashicorp
  defined_tags   = each.value.defined_tags
  display_name   = each.value.igw_name != null ? each.value.igw_name : null
  freeform_tags  = each.value.freeform_tags
  route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ? (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.gateway-route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null

}

/*
output "igw_id_map" {
  value = [ for k,v in merge(module.igws.*...) : v.igw_id ]
}
*/

############################
# Module Block - Network
# Create NAT Gateways
############################

module "ngws" {
  source   = "./modules/network/ngw"
  for_each = (var.ngws != null || var.ngws != {}) ? var.ngws : {}

  depends_on = [module.vcns]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  block_traffic  = each.value.block_traffic # Defaults to false by terraform hashicorp
  public_ip_id   = each.value.public_ip_id
  route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ? (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.gateway-route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null

  defined_tags  = each.value.defined_tags
  display_name  = each.value.ngw_name
  freeform_tags = each.value.freeform_tags
}

/*
output "ngw_id_map" {
  value = [ for k,v in merge(module.ngws.*...) : v.ngw_id ]
}
*/

############################
# Module Block - Network
# Create Service Gateways
############################

module "sgws" {
  source   = "./modules/network/sgw"
  for_each = (var.sgws != null || var.sgws != {}) ? var.sgws : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  defined_tags   = each.value.defined_tags
  display_name   = each.value.sgw_name != null ? each.value.sgw_name : null
  freeform_tags  = each.value.freeform_tags
  service        = each.value.service != "" ? (contains(split("-", each.value.service), "all") == true ? "all" : "objectstorage") : "all"
  route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ? (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.gateway-route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null
}

/*
output "sgw_id_map" {
  value = [ for k,v in merge(module.sgws.*...) : v.sgw_id ]
}
*/


############################
# Module Block - Networking
# Create Local Peering Gateways
############################

module "hub-lpgs" {
  source   = "./modules/network/lpg"
  for_each = (var.lpgs.hub-lpgs != null || var.lpgs.hub-lpgs != {}) ? var.lpgs.hub-lpgs : {}

  depends_on = [module.vcns, module.spoke-lpgs, module.none-lpgs, module.exported-lpgs, module.peer-lpgs]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  peer_id = each.value.peer_id != "" ? (length(regexall("##peer_id*", each.value.peer_id)) > 0 ? null : try(merge(module.spoke-lpgs.*...)[each.value.peer_id]["lpg_tf_id"], merge(module.exported-lpgs.*...)[each.value.peer_id]["lpg_tf_id"], merge(module.peer-lpgs.*...)[each.value.peer_id]["lpg_tf_id"], merge(module.none-lpgs.*...)[each.value.peer_id]["lpg_tf_id"])) : null
  #route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ?  (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null
  defined_tags  = each.value.defined_tags
  display_name  = each.value.lpg_name != null ? each.value.lpg_name : null
  freeform_tags = each.value.freeform_tags
}

module "spoke-lpgs" {
  source   = "./modules/network/lpg"
  for_each = (var.lpgs.spoke-lpgs != null || var.lpgs.spoke-lpgs != {}) ? var.lpgs.spoke-lpgs : {}

  depends_on = [module.vcns]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  peer_id = (each.value.peer_id != "" && each.value.peer_id != null) ? (length(regexall("##peer_id*", each.value.peer_id)) > 0 ? null : each.value.peer_id) : null
  #route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ?  (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null
  defined_tags  = each.value.defined_tags
  display_name  = each.value.lpg_name != null ? each.value.lpg_name : null
  freeform_tags = each.value.freeform_tags
}

module "peer-lpgs" {
  source   = "./modules/network/lpg"
  for_each = (var.lpgs.peer-lpgs != null || var.lpgs.peer-lpgs != {}) ? var.lpgs.peer-lpgs : {}

  depends_on = [module.vcns, module.none-lpgs]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  peer_id = each.value.peer_id != "" ? (length(regexall("##peer_id*", each.value.peer_id)) > 0 ? null : try(merge(module.spoke-lpgs.*...)[each.value.peer_id]["lpg_tf_id"], merge(module.exported-lpgs.*...)[each.value.peer_id]["lpg_tf_id"], merge(module.none-lpgs.*...)[each.value.peer_id]["lpg_tf_id"])) : null
  #route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ?  (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null
  defined_tags  = each.value.defined_tags
  display_name  = each.value.lpg_name != null ? each.value.lpg_name : null
  freeform_tags = each.value.freeform_tags
}

module "none-lpgs" {
  source   = "./modules/network/lpg"
  for_each = (var.lpgs.none-lpgs != null || var.lpgs.none-lpgs != {}) ? var.lpgs.none-lpgs : {}

  depends_on = [module.vcns]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  peer_id = (each.value.peer_id != "" && each.value.peer_id != null) ? (length(regexall("##peer_id*", each.value.peer_id)) > 0 ? null : each.value.peer_id) : null
  #route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ?  (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null
  defined_tags  = each.value.defined_tags
  display_name  = each.value.lpg_name != null ? each.value.lpg_name : null
  freeform_tags = each.value.freeform_tags
}

module "exported-lpgs" {
  source   = "./modules/network/lpg"
  for_each = (var.lpgs.exported-lpgs != null || var.lpgs.exported-lpgs != {}) ? var.lpgs.exported-lpgs : {}

  depends_on = [module.vcns]

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  #Optional
  peer_id = (each.value.peer_id != "" && each.value.peer_id != null) ? (length(regexall("##peer_id*", each.value.peer_id)) > 0 ? null : each.value.peer_id) : null
  #route_table_id = (each.value.route_table_id != "" && each.value.route_table_id != null) ?  (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(module.route-tables.*...)[each.value.route_table_id]["route_table_ids"]) : null
  defined_tags  = each.value.defined_tags
  display_name  = each.value.lpg_name != null ? each.value.lpg_name : null
  freeform_tags = each.value.freeform_tags
}

/*
output "hub_lpg_id_map" {
  value = [ for k,v in merge(module.hub-lpgs.*...) : v.lpg_id ]
}

output "spoke_lpg_id_map" {
  value = [ for k,v in merge(module.spoke-lpgs.*...) : v.lpg_id ]
}

output "peer_lpg_id_map" {
  value = [ for k,v in merge(module.peer-lpgs.*...) : v.lpg_id ]
}

output "none_lpg_id_map" {
  value = [ for k,v in merge(module.none-lpgs.*...) : v.lpg_id ]
}

output "exported_lpg_id_map" {
  value = [ for k,v in merge(module.exported-lpgs.*...) : v.lpg_id ]
}
*/

############################
# Module Block - Network
# Create Dynamic Routing Gateways
############################

module "drgs" {
  #Required
  source   = "./modules/network/drg"
  for_each = (var.drgs != null || var.drgs != {}) ? var.drgs : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  defined_tags  = each.value.defined_tags
  display_name  = each.value.display_name
  freeform_tags = each.value.freeform_tags
}


module "drg-attachments" {
  #Required
  source   = "./modules/network/drg-attachment"
  for_each = (var.drg_attachments != null || var.drg_attachments != {}) ? var.drg_attachments : {}

  drg_display_name   = each.value.display_name
  defined_tags       = each.value.defined_tags
  freeform_tags      = each.value.freeform_tags
  drg_id             = length(regexall("ocid1.drg.oc*", each.value.drg_id)) > 0 ? each.value.drg_id : ((each.value.drg_id != "" && each.value.drg_id != null) ? merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"] : each.value.drg_id)
  drg_route_table_id = length(regexall("ocid1.drgroutetable.oc*", each.value.drg_route_table_id)) > 0 ? each.value.drg_route_table_id : ((each.value.drg_route_table_id != "" && each.value.drg_route_table_id != null) ? merge(module.drg-route-tables.*...)[each.value.drg_route_table_id]["drg_route_table_tf_id"] : null)
  vcns_tf_id         = merge(module.vcns.*...)
  route_table_tf_id  = merge(module.route-tables.*...)
  #default_route_table_tf_id = merge(module.default-route-tables.*...)
  drg_attachments = var.drg_attachments
  key_name        = each.key
}


/*
output "drg_id_map" {
  value = [ for k,v in merge(module.drg.*...) : v.drg_id ]
}

output "drg_attachments_map" {
  value = [ for k,v in merge(module.drg-attachments.*...) : v.drg_attachments_map ]
}
*/

############################
# Module Block - Network
# Create Default DHCP
############################

module "default-dhcps" {
  #Required
  source   = "./modules/network/default-dhcp"
  for_each = (var.default_dhcps != null || var.default_dhcps != {}) ? var.default_dhcps : {}

  #Required
  manage_default_resource_id = length(regexall("ocid1.dhcpoptions.oc*", each.value.manage_default_resource_id)) > 0 ? each.value.manage_default_resource_id : merge(module.vcns.*...)[each.value.manage_default_resource_id]["vcn_default_dhcp_id"]
  server_type                = each.value.server_type
  custom_dns_servers         = each.value.custom_dns_servers
  search_domain_names        = each.value.search_domain != null ? each.value.search_domain.names : []

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "default_dhcp_id" {
  value = [ for k,v in merge(module.default-dhcps.*...) : v.default_dhcp_id ]
}
*/

############################
# Module Block - Network
# Create Custom DHCP Options
############################

module "custom-dhcps" {
  #Required
  source   = "./modules/network/custom-dhcp"
  for_each = (var.custom_dhcps != null || var.custom_dhcps != {}) ? var.custom_dhcps : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  server_type         = each.value.server_type
  custom_dns_servers  = each.value.custom_dns_servers != null ? each.value.custom_dns_servers : []
  search_domain_names = each.value.search_domain

  #Optional
  defined_tags     = each.value.defined_tags
  display_name     = each.value.display_name
  domain_name_type = each.value.domain_name_type
  freeform_tags    = each.value.freeform_tags
}

/*
output "dhcp_options_id" {
  value = [ for k,v in merge(module.custom-dhcps.*...) : v.custom_dhcp_id ]
}
*/

############################
# Module Block - Network
# Create Default Security Lists
############################

/*
output "default_seclist_id_map" {
  value = [ for k,v in merge(module.default-security-lists.*...) : v.default_seclist_id ]
}
*/

############################
# Module Block - Network
# Create Custom Security Lists
############################

module "security-lists" {
  source   = "./modules/network/sec-list"
  for_each = (local.all_seclists != null || local.all_seclists != {}) ? local.all_seclists : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  vcn_id                     = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]
  manage_default_resource_id = merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_security_list_id"]
  default_seclist            = var.default_seclists != {} ? contains(keys(var.default_seclists), each.key) ? true : false : false

  key_name        = each.key
  defined_tags    = each.value.defined_tags
  display_name    = each.value.display_name != null ? each.value.display_name : null
  freeform_tags   = each.value.freeform_tags
  seclist_details = local.all_seclists
}

/*
output "seclist_id_map" {
  value = [ for k,v in merge(module.security-lists.*...) : v.seclist_id ]
}
*/

############################
# Module Block - Network
# Create Custom Route Tables
############################

module "route-tables" {
  source = "./modules/network/route-table"
  #for_each = {for k,v in local.all_route_tables : k => v if ! v.gateway_route_table}
  for_each = { for k, v in local.all_route_tables : k => v if !local.gateway_rt_status[k] }

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  default_route_table        = var.default_route_tables != {} ? contains(keys(var.default_route_tables), each.key) ? true : false : false
  manage_default_resource_id = merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_route_table_id"]

  #Optional
  defined_tags    = each.value.defined_tags
  display_name    = each.value.display_name != null ? each.value.display_name : null
  freeform_tags   = each.value.freeform_tags
  key_name        = each.key
  igw_id          = merge(module.igws.*...)
  ngw_id          = merge(module.ngws.*...)
  sgw_id          = merge(module.sgws.*...)
  drg_id          = merge(module.drgs.*...)
  hub_lpg_id      = merge(module.hub-lpgs.*...)
  spoke_lpg_id    = merge(module.spoke-lpgs.*...)
  peer_lpg_id     = merge(module.peer-lpgs.*...)
  none_lpg_id     = merge(module.none-lpgs.*...)
  exported_lpg_id = merge(module.exported-lpgs.*...)
  rt_details      = local.all_route_tables
}


module "gateway-route-tables" {
  source = "./modules/network/route-table"
  #for_each = {for k,v in local.all_route_tables : k => v if v.gateway_route_table }
  for_each = { for k, v in local.all_route_tables : k => v if local.gateway_rt_status[k] }

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]

  default_route_table        = var.default_route_tables != {} ? contains(keys(var.default_route_tables), each.key) ? true : false : false
  manage_default_resource_id = merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_route_table_id"]
  #Optional
  defined_tags        = each.value.defined_tags
  display_name        = each.value.display_name != null ? each.value.display_name : null
  freeform_tags       = each.value.freeform_tags
  key_name            = each.key
  drg_id              = merge(module.drgs.*...)
  rt_details          = local.all_route_tables
  gateway_route_table = each.value.gateway_route_table
}

/*
output "route_id_map" {
  value = [ for k,v in merge(module.route-tables.*...) : v.route_id ]
}
*/


############################
# Module Block - Network
# Create DRG Route Tables
############################

module "drg-route-tables" {
  source   = "./modules/network/drg-route-table"
  for_each = (var.drg_route_tables != null || var.drg_route_tables != {}) ? var.drg_route_tables : {}

  #Required
  drg_id = each.value.drg_id != null && each.value.drg_id != "" ? (length(regexall("ocid1.drg.oc*", each.value.drg_id)) > 0 ? each.value.drg_id : merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"]) : null

  #Optional
  defined_tags                     = each.value.defined_tags == {} ? null : each.value.defined_tags
  freeform_tags                    = each.value.freeform_tags == {} ? null : each.value.freeform_tags
  display_name                     = each.value.display_name != null ? each.value.display_name : null
  import_drg_route_distribution_id = each.value.import_drg_route_distribution_id != null && each.value.import_drg_route_distribution_id != "" ? (length(regexall("ocid1.drgroutedistribution.oc*", each.value.import_drg_route_distribution_id)) > 0 ? each.value.import_drg_route_distribution_id : (length(regexall(".Autogenerated-Import-Route-Distribution-for*", each.value.import_drg_route_distribution_id)) > 0 ? data.oci_core_drg_route_distributions.drg_route_distributions[each.value.import_drg_route_distribution_id].drg_route_distributions[0].id : merge(module.drg-route-distributions.*...)[each.value.import_drg_route_distribution_id]["drg_route_distribution_tf_id"])) : null
  is_ecmp_enabled                  = each.value.is_ecmp_enabled != null ? each.value.is_ecmp_enabled : null
}

/*
output "drg_route_id_map" {
  value = [ for k,v in merge(module.drg-route-tables.*...) : v.drg_route_tf_id ]
}
*/

################################
# Module Block - Network
# Create DRG Route Rules
################################

module "drg-route-rules" {
  source     = "./modules/network/drg-route-rule"
  depends_on = [module.drg-attachments, module.drg-route-tables]

  for_each = (var.drg_route_rules != null || var.drg_route_rules != {}) ? var.drg_route_rules : {}

  #Required
  drg_route_table_id         = length(regexall("ocid1.drgroutetable.oc*", each.value.drg_route_table_id)) > 0 ? each.value.drg_route_table_id : ((each.value.drg_route_table_id != "" && each.value.drg_route_table_id != null) ? (length(regexall(".Autogenerated-Drg-Route-Table-for*", each.value.drg_route_table_id)) > 0 ? data.oci_core_drg_route_tables.drg_route_tables[each.value.drg_route_table_id].drg_route_tables[0].id : merge(module.drg-route-tables.*...)[each.value.drg_route_table_id]["drg_route_table_tf_id"]) : null)
  destination                = each.value.destination
  destination_type           = each.value.destination_type
  next_hop_drg_attachment_id = length(regexall("ocid1.drgattachment.oc*", each.value.next_hop_drg_attachment_id)) > 0 ? each.value.next_hop_drg_attachment_id : (each.value.next_hop_drg_attachment_id != "" && each.value.next_hop_drg_attachment_id != null ? merge(module.drg-attachments.*...)[each.value.next_hop_drg_attachment_id]["drg_attachment_tf_id"] : null)


}

/*
output "drg_route_rules_id_map" {
  value = [ for k,v in merge(module.drg-route-rules.*...) : v.drg_route_rule_tf_id ]
}
*/


################################
# Module Block - Network
# Create DRG Route Distributions
################################

module "drg-route-distributions" {
  source   = "./modules/network/drg-route-distribution"
  for_each = (var.drg_route_distributions != null || var.drg_route_distributions != {}) ? var.drg_route_distributions : {}

  #Required
  distribution_type = each.value.distribution_type
  drg_id            = each.value.drg_id != null && each.value.drg_id != "" ? (length(regexall("ocid1.drg.oc*", each.value.drg_id)) > 0 ? each.value.drg_id : merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"]) : null

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  display_name  = each.value.display_name
}

/*
output "drg_route_distributions_id_map" {
  value = [ for k,v in merge(module.drg-route-distributions.*...) : v.drg_route_distribution_tf_id ]
}
*/

###########################################
# Module Block - Network
# Create DRG Route Distribution Statements
###########################################

module "drg-route-distribution-statements" {
  source   = "./modules/network/drg-route-distribution-statement"
  for_each = (var.drg_route_distribution_statements != null || var.drg_route_distribution_statements != {}) ? var.drg_route_distribution_statements : {}

  #Required
  key_name                          = each.key
  drg_route_distribution_id         = each.value.drg_route_distribution_id != null && each.value.drg_route_distribution_id != "" ? (length(regexall("ocid1.drgroutedistribution.oc*", each.value.drg_route_distribution_id)) > 0 ? each.value.drg_route_distribution_id : (length(regexall(".Autogenerated-Import-Route-Distribution-for*", each.value.drg_route_distribution_id)) > 0 ? data.oci_core_drg_route_distributions.drg_route_distributions[each.value.drg_route_distribution_id].drg_route_distributions[0].id : merge(module.drg-route-distributions.*...)[each.value.drg_route_distribution_id]["drg_route_distribution_tf_id"])) : null
  priority                          = each.value.priority
  action                            = each.value.action
  drg_attachment_ids                = merge(module.drg-attachments.*...)
  drg_route_distribution_statements = var.drg_route_distribution_statements
}

/*
output "drg_route_distribution_statements_id_map" {
  value = [ for k,v in merge(module.drg-route-distribution-statements.*...) : v.drg_route_distribution_statement_tf_id ]
}
*/

#############################
# Module Block - Network
# Create Subnets
#############################

module "subnets" {
  source   = "./modules/network/subnet"
  for_each = (var.subnets != null || var.subnets != {}) ? var.subnets : {}

  depends_on = [module.vcns, module.security-lists]

  #Required
  tenancy_ocid   = var.tenancy_ocid
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_id)) > 0 ? each.value.vcn_id : merge(module.vcns.*...)[each.value.vcn_id]["vcn_tf_id"]
  cidr_block     = each.value.cidr_block

  #Optional
  dns_label                  = each.value.dns_label
  ipv6cidr_block             = each.value.ipv6cidr_block
  defined_tags               = each.value.defined_tags
  display_name               = each.value.display_name
  freeform_tags              = each.value.freeform_tags
  prohibit_internet_ingress  = each.value.prohibit_internet_ingress
  prohibit_public_ip_on_vnic = each.value.prohibit_public_ip_on_vnic
  availability_domain        = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  dhcp_options_id            = each.value.dhcp_options_id == null || each.value.dhcp_options_id == "" ? merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_dhcp_id"] : (length(regexall("ocid1.dhcpoptions.oc*", each.value.dhcp_options_id)) > 0 ? each.value.dhcp_options_id : merge(module.custom-dhcps.*...)[each.value.dhcp_options_id]["custom_dhcp_tf_id"])
  #route_table_id              = each.value.route_table_id == null || each.value.route_table_id == "" ? merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_route_table_id"] : (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : contains(keys(merge(module.gateway-route-tables.*...)), each.value.route_table_id) ? merge(module.gateway-route-tables.*...)[each.value.route_table_id] ["route_table_ids"] : merge(module.route-tables.*...)[each.value.route_table_id]["route_table_ids"])
  route_table_id = each.value.route_table_id == null || each.value.route_table_id == "" ? merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_route_table_id"] : (length(regexall("ocid1.routetable.oc*", each.value.route_table_id)) > 0 ? each.value.route_table_id : merge(merge(module.gateway-route-tables.*...), merge(module.route-tables.*...))[each.value.route_table_id]["route_table_ids"])


  security_list_ids            = length(each.value.security_list_ids) == 0 ? [merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_security_list_id"]] : each.value.security_list_ids
  vcn_default_security_list_id = merge(module.vcns.*...)[each.value.vcn_id]["vcn_default_security_list_id"]
  custom_security_list_id      = merge(module.security-lists.*...)
}

/*
output "subnet_id_map" {
  value = [ for k,v in merge(module.subnets.*...) : v.subnet_id ]
}
*/

#############################
# Module Block - Network Logging
# Create VCN Log Groups and Logs
#############################

module "vcn-log-groups" {
  source   = "./modules/managementservices/log-group"
  for_each = (var.vcn_log_groups != null || var.vcn_log_groups != {}) ? var.vcn_log_groups : {}

  # Log Groups
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  display_name = each.value.display_name

  #Optional
  defined_tags  = each.value.defined_tags
  description   = each.value.description
  freeform_tags = each.value.freeform_tags
}

/*
output "vcn_log_group_map" {
  value = [ for k,v in merge(module.vcn-log-groups.*...) : v.log_group_tf_id ]
}
*/

module "vcn-logs" {
  source   = "./modules/managementservices/log"
  for_each = (var.vcn_logs != null || var.vcn_logs != {}) ? var.vcn_logs : {}

  # Logs
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.display_name
  log_group_id   = length(regexall("ocid1.loggroup.oc*", each.value.log_group_id)) > 0 ? each.value.log_group_id : merge(module.vcn-log-groups.*...)[each.value.log_group_id]["log_group_tf_id"]

  log_type = each.value.log_type
  #Required
  source_category        = each.value.category
  source_resource        = length(regexall("ocid1.*", each.value.resource)) > 0 ? each.value.resource : merge(module.subnets.*...)[each.value.resource]["subnet_tf_id"]
  source_service         = each.value.service
  source_type            = each.value.source_type
  defined_tags           = each.value.defined_tags
  freeform_tags          = each.value.freeform_tags
  log_is_enabled         = (each.value.is_enabled == "" || each.value.is_enabled == null) ? true : each.value.is_enabled
  log_retention_duration = (each.value.retention_duration == "" || each.value.retention_duration == null) ? 30 : each.value.retention_duration

}

/*
output "vcn_logs_id" {
  value = [ for k,v in merge(module.vcn-logs.*...) : v.log_tf_id]
}
*/