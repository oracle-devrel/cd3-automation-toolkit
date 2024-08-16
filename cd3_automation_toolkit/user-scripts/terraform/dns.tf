# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
####################
### DNS-Resolver ###
####################


data "oci_core_vcn_dns_resolver_association" "resolver_vcn_dns_resolver_association" {
  for_each = var.resolvers != null ? var.resolvers : {}
  vcn_id   = data.oci_core_vcns.resolver_oci_vcns[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "resolver_oci_vcns" {
  # depends_on = [module.vcns] # Uncomment to create resolver and vcn together
  for_each       = var.resolvers != null ? var.resolvers : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

### Data for Subnet ###

locals {
  subnets = flatten([
    for resolver_key, res in var.resolvers : [
      for e_key, endpoint in res.endpoint_names : {
        vcn_name               = res.vcn_name
        network_compartment_id = res.network_compartment_id
        subnet_name            = endpoint.subnet_name
        #subnet_name = trimprefix("${endpoint.subnet_name}", "${res.vcn_name}_")
        resolver_key  = resolver_key
        endpoint_name = endpoint.name
      }
    ]
  ])
}

data "oci_core_subnets" "resolver_oci_subnets" {
  # depends_on = [module.subnets] # Uncomment to create resolver and subnets together
  for_each       = { for sn in local.subnets : "${sn.endpoint_name}_${sn.subnet_name}" => sn }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_name
  vcn_id         = data.oci_core_vcns.resolver_oci_vcns[each.value.resolver_key].virtual_networks.*.id[0]
}
### Data for NSGs###

locals {
  nsgs = flatten([
    for resolver_key, res in var.resolvers : [
      for e_key, endpoint in res.endpoint_names : [
        for nsg in endpoint.nsg_ids : {
          vcn_name               = res.vcn_name
          network_compartment_id = res.network_compartment_id
          nsg_name               = nsg
          resolver_key           = resolver_key
          endpoint_name          = endpoint.name
        }
      ]
    ]
  ])
}
data "oci_core_network_security_groups" "resolver_network_security_groups" {
  for_each       = { for nsg in local.nsgs : "${nsg.endpoint_name}_${nsg.nsg_name}" => nsg }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.nsg_name
  vcn_id         = data.oci_core_vcns.resolver_oci_vcns[each.value.resolver_key].virtual_networks.*.id[0]
}
### Data for Views ###
locals {
  resolver_views = flatten([
    for resolver_key, res in var.resolvers : [
      for view_key, view in res.views : {
        resolver_key     = resolver_key
        view_key         = view_key
        view_name        = view.view_id
        view_compartment = view.view_compartment_id
      }
    ]
  ])
}

data "oci_dns_views" "resolver_views_data" {
  #Required
  for_each       = { for rv in local.resolver_views : "${rv.view_key}" => rv }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.view_compartment)) > 0 ? each.value.view_compartment : var.compartment_ocids[each.value.view_compartment]
  scope          = "PRIVATE"
  #Optional
  display_name = each.value.view_name
  state        = "ACTIVE"
}

### Module ###
module "dns-resolvers" {
  source = "./modules/network/dns/dns_resolver"
  # depends_on = [module.nsgs] # Uncomment to create NSG and DNS Resolvers together
  for_each              = var.resolvers != null ? var.resolvers : {}
  target_resolver_id    = data.oci_core_vcn_dns_resolver_association.resolver_vcn_dns_resolver_association[each.key].*.dns_resolver_id[0]
  resolver_scope        = "PRIVATE"
  resolver_display_name = each.value.display_name != null ? each.value.display_name : null
  views = each.value.views != null ? {
    for v_key, view in each.value.views : v_key => {
      view_id = length(regexall("ocid1.dnsview.oc*", view.view_id)) > 0 ? view.view_id : try(data.oci_dns_views.resolver_views_data["${v_key}"].views.*.id[0], module.dns-views[view.view_id]["dns_view_id"])
    }
  } : null

  resolver_rules         = each.value.resolver_rules != null ? each.value.resolver_rules : null
  resolver_defined_tags  = try(each.value.defined_tags, null)
  resolver_freeform_tags = try(each.value.freeform_tags, null)
  endpoint_names = each.value.endpoint_names != null ? {
    for key, endpoint in each.value.endpoint_names : key => {
      forwarding = endpoint.is_forwarding
      listening  = endpoint.is_listening
      name       = endpoint.name
      #resolver_id = oci_dns_resolver.test_resolver.id
      subnet_id = length(regexall("ocid1.subnet.oc*", endpoint.subnet_name)) > 0 ? endpoint.subnet_name : data.oci_core_subnets.resolver_oci_subnets["${endpoint.name}_${endpoint.subnet_name}"].subnets.*.id[0]
      scope     = "PRIVATE"

      #Optional
      endpoint_type      = "VNIC"
      forwarding_address = endpoint.forwarding_address
      listening_address  = endpoint.listening_address
      nsg_ids            = endpoint.nsg_ids != null ? flatten(tolist([for nsg in endpoint.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.resolver_network_security_groups["${endpoint.name}_${nsg}"].network_security_groups[*].id)])) : null

    }
  } : null

}

##################
### DNS-RRsets ###
##################
data "oci_dns_views" "rrset_views_data" {
  #Required
  for_each       = var.rrsets
  compartment_id = each.value.view_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.view_compartment_id)) > 0 ? each.value.view_compartment_id : var.compartment_ocids[each.value.view_compartment_id]) : null
  scope          = "PRIVATE"

  #Optional
  display_name = each.value.view_id
  state        = "ACTIVE"
}

data "oci_dns_zones" "rrset_zones_data" {
  for_each       = { for k, v in var.rrsets : k => v if try(data.oci_dns_views.rrset_views_data[k].views.*.id[0], 0) != 0 }
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  name    = each.value.zone_id
  scope   = "PRIVATE"
  state   = "ACTIVE"
  view_id = length(regexall("ocid1.dnsview.oc*", each.value.view_id)) > 0 ? each.value.view_id : try(data.oci_dns_views.rrset_views_data[each.key].views.*.id[0], module.dns-views[each.value.view_id]["dns_view_id"])
}

module "dns-rrsets" {
  source     = "./modules/network/dns/rrset"
  for_each   = var.rrsets != null ? var.rrsets : {}
  depends_on = [module.dns-views, module.dns-zones]
  rrset_zone = try(data.oci_dns_zones.rrset_zones_data[each.key].zones.*.id[0], module.dns-zones[join("_", [each.value.view_id, replace(each.value.zone_id, ".", "_")])]["dns_zone_id"])
  #rrset_view_id        = each.value.view_id != "" ? (length(regexall("ocid1.dnsview.oc*", each.value.view_id)) > 0 ? each.value.view_id : data.oci_dns_views.rrset_views_data[each.key].views.*.id[0]) : null
  rrset_view_id = length(regexall("ocid1.dnsview.oc*", each.value.view_id)) > 0 ? each.value.view_id : try(data.oci_dns_views.rrset_views_data[each.key].views.*.id[0], module.dns-views[each.value.view_id]["dns_view_id"])
  rrset_domain  = each.value.domain
  rrset_rtype   = each.value.rtype
  rrset_ttl     = each.value.ttl
  #rrset_compartment_id   = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  rrset_rdata = each.value.rdata
  rrset_scope = "PRIVATE"

}
#output "zone_id" {
#value = { for key, value in var.rrsets: key =>  module.dns-zones[join("_", [value.view_id,replace(value.zone_id, ".", "_")])]["dns_zone_id"]}
#}
#
#output "zone_data" {
#value = { for key, value in var.rrsets: key =>  data.oci_dns_zones.rrset_zones_data[key].zones.*.id[0]}
#}

#################
### DNS-Zones ###
#################
data "oci_dns_views" "zone_views_data" {
  #Required
  for_each       = { for k, v in var.zones : k => v if v.view_id != null }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.view_compartment_id)) > 0 ? each.value.view_compartment_id : var.compartment_ocids[each.value.view_compartment_id]
  scope          = "PRIVATE"
  display_name   = each.value.view_id
  state          = "ACTIVE"
}

module "dns-zones" {
  source              = "./modules/network/dns/zone"
  depends_on          = [module.dns-views]
  for_each            = { for k, v in var.zones : k => v if var.zones != null }
  zone_compartment_id = length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]
  zone_name           = each.value.display_name
  zone_type           = "PRIMARY"
  zone_defined_tags   = try(each.value.defined_tags, null)
  zone_freeform_tags  = try(each.value.freeform_tags, null)
  #external_masters       = each.value.external_masters != null ? each.value.external_masters : {}
  zone_scope = "PRIVATE"
  view_id    = length(regexall("ocid1.dnsview.oc*", each.value.view_id)) > 0 ? each.value.view_id : try(data.oci_dns_views.zone_views_data[each.key].views.*.id[0], module.dns-views[each.value.view_id]["dns_view_id"])
}

#################
### DNS-Views ###
#################

module "dns-views" {
  source              = "./modules/network/dns/view"
  for_each            = var.views != null ? var.views : {}
  view_compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  view_display_name   = each.value.display_name
  view_scope          = try((each.value.scope != null ? (each.value.scope == "PRIVATE" ? each.value.scope : null) : null), null)
  view_defined_tags   = try(each.value.defined_tags, null)
  view_freeform_tags  = try(each.value.freeform_tags, null)

}