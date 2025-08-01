# Copyright (c) 2025, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
####################
### DNS-Resolver ###
####################
locals {
  resolver_vcns = {
    for item_key, item_value in var.resolvers : "${item_value.vcn_name}" => (length(regexall("ocid1.compartment.oc*", item_value.network_compartment_id)) > 0 ? item_value.network_compartment_id : var.compartment_ocids[item_value.network_compartment_id])...
  }
  resolver_vcns_distinct = { for k, v in local.resolver_vcns : k => distinct(v)[0] }
}

data "oci_core_vcns" "dns_oci_vcns" {
  for_each       = local.resolver_vcns_distinct
  compartment_id = each.value != null ? (length(regexall("ocid1.compartment.oc*", each.value)) > 0 ? each.value : var.compartment_ocids[each.value]) : null
  display_name   = each.key
}

data "oci_core_vcn_dns_resolver_association" "resolver_vcn_dns_resolver_association" {
  for_each = local.resolver_vcns_distinct
  vcn_id   = data.oci_core_vcns.dns_oci_vcns[each.key].virtual_networks.*.id[0]
}

### Data for Subnet ###

locals {
  endpoint_subnets = distinct(flatten([
    for resolver_key, res in var.resolvers : [
      for e_key, endpoint in res.endpoint_names : {
        vcn_name               = res.vcn_name
        network_compartment_id = length(regexall("ocid1.compartment.oc*", res.network_compartment_id)) > 0 ? res.network_compartment_id : var.compartment_ocids[res.network_compartment_id]
        subnet_name            = endpoint.subnet_name
      }
    ]
  ]))
}
data "oci_core_subnets" "dns_oci_subnets" {
  for_each       = { for item in local.endpoint_subnets : item.subnet_name => item if length(regexall("ocid1.subnet.oc*", item.subnet_name)) == 0 }
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  display_name   = each.key
  vcn_id         = data.oci_core_vcns.dns_oci_vcns[each.value.vcn_name].virtual_networks.*.id[0]
}

### Data for NSGs###

locals {
  nsgs = distinct(flatten([
    for resolver_key, res in var.resolvers : [
      for e_key, endpoint in res.endpoint_names : [
        for nsg in endpoint.nsg_ids : {
          vcn_name               = res.vcn_name
          network_compartment_id = length(regexall("ocid1.compartment.oc*", res.network_compartment_id)) > 0 ? res.network_compartment_id : var.compartment_ocids[res.network_compartment_id]
          nsg_name               = nsg
        }
      ]
    ]
  ]))
}

data "oci_core_network_security_groups" "endpoint_nsgs" {
  for_each       = { for nsg in local.nsgs : nsg.nsg_name => nsg if length(regexall("ocid1.networksecuritygroup.oc*", nsg.nsg_name)) == 0 }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.nsg_name
  vcn_id         = data.oci_core_vcns.dns_oci_vcns[each.value.vcn_name].virtual_networks.*.id[0]
}

### Data for Views ###
locals {
  resolver_views = distinct(flatten([
    for resolver_key, res in var.resolvers : [
      for view_key, view in res.views : {
        view_name        = view.view_id
        view_compartment = length(regexall("ocid1.compartment.oc*", view.view_compartment_id)) > 0 ? view.view_compartment_id : var.compartment_ocids[view.view_compartment_id]
      }
    ]
  ]))
  zone_views = distinct([for k, v in var.zones : {
    view_name        = v.view_id
    view_compartment = length(regexall("ocid1.compartment.oc*", v.view_compartment_id)) > 0 ? v.view_compartment_id : var.compartment_ocids[v.view_compartment_id]
  }])
  rrset_views = distinct([for k, v in var.rrsets : {
    view_name        = v.view_id
    view_compartment = length(regexall("ocid1.compartment.oc*", v.view_compartment_id)) > 0 ? v.view_compartment_id : var.compartment_ocids[v.view_compartment_id]
  }])
  all_views = distinct(concat(local.resolver_views, local.zone_views, local.rrset_views))
}

data "oci_dns_views" "all_views_data" {
  #Required
  for_each       = { for rv in local.all_views : "${rv.view_name}" => rv if length(regexall("ocid1.dnsview.oc*", rv.view_name)) == 0 }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.view_compartment)) > 0 ? each.value.view_compartment : var.compartment_ocids[each.value.view_compartment]
  scope          = "PRIVATE"
  #Optional
  display_name = each.value.view_name
  state        = "ACTIVE"
}


### Module ###
module "dns-resolvers" {
  source                = "./modules/network/dns/dns_resolver"
  for_each              = var.resolvers != null ? var.resolvers : {}
  target_resolver_id    = data.oci_core_vcn_dns_resolver_association.resolver_vcn_dns_resolver_association[each.key].*.dns_resolver_id[0]
  resolver_scope        = "PRIVATE"
  resolver_display_name = each.value.display_name != null ? each.value.display_name : null
  views = each.value.views != null ? {
    for v_key, view in each.value.views : v_key => {
      view_id = length(regexall("ocid1.dnsview.oc*", view.view_id)) > 0 ? view.view_id : try(data.oci_dns_views.all_views_data[view.view_id].views.*.id[0], module.dns-views[view.view_id].views.*.id[0])
      #view_id = length(regexall("ocid1.dnsview.oc*", view.view_id)) > 0 ? view.view_id : merge(data.oci_dns_views.all_views_data[view.view_id], module.dns-views[view.view_id]).views.*.id[0]
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
      subnet_id = length(regexall("ocid1.subnet.oc*", endpoint.subnet_name)) > 0 ? endpoint.subnet_name : data.oci_core_subnets.dns_oci_subnets[endpoint.subnet_name].subnets.*.id[0]
      scope     = "PRIVATE"

      #Optional
      endpoint_type      = "VNIC"
      forwarding_address = endpoint.forwarding_address
      listening_address  = endpoint.listening_address
      nsg_ids            = endpoint.nsg_ids != null ? flatten(tolist([for nsg in endpoint.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.endpoint_nsgs[nsg].network_security_groups[*].id)])) : null

    }
  } : null

}

##################
### DNS-RRsets ###
##################


locals {

  rrset_zones = {
    for item_key, item_value in var.rrsets : "${item_value.view_id}_${item_value.zone_id}" => { "comp" = "${item_value.compartment_id}", "zone_name" = "${item_value.zone_id}", "view" = "${item_value.view_id}" }...
  }
  rrset_zone_distinct = { for k, v in local.rrset_zones : k => distinct(v)[0] }
}


data "oci_dns_zones" "rrset_zones_data" {
  for_each       = { for z, z_data in local.rrset_zone_distinct : z => z_data if length(regexall("ocid1.dnszone.oc*", z_data.zone_name)) == 0 }
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.comp)) > 0 ? each.value.comp : var.compartment_ocids[each.value.comp]

  #Optional
  name    = each.value.zone_name
  scope   = "PRIVATE"
  state   = "ACTIVE"
  view_id = length(regexall("ocid1.dnsview.oc*", each.value.view)) > 0 ? each.value.view : try(data.oci_dns_views.all_views_data[each.value.view].views.*.id[0], module.dns-views[each.value.view]["views"].*.id[0])
}

module "dns-rrsets" {
  source     = "./modules/network/dns/rrset"
  for_each   = var.rrsets != null ? var.rrsets : {}
  #depends_on = [module.dns-views, module.dns-zones]
  rrset_zone = length(regexall("ocid1.dnszone.oc*", each.value.zone_id)) > 0 ? each.value.zone_id : try(data.oci_dns_zones.rrset_zones_data["${each.value.view_id}_${each.value.zone_id}"].zones.*.id[0],module.dns-zones[join("_", [each.value.view_id, replace(each.value.zone_id, ".", "_")])].zones.*.id[0])
  rrset_view_id = length(regexall("ocid1.dnsview.oc*", each.value.view_id)) > 0 ? each.value.view_id : try(data.oci_dns_views.all_views_data[each.value.view_id].views.*.id[0], module.dns-views[each.value.view_id].views.*.id[0])
  rrset_domain  = each.value.domain
  rrset_rtype   = each.value.rtype
  rrset_ttl     = each.value.ttl
  rrset_rdata   = each.value.rdata
  rrset_scope   = "PRIVATE"

}

#################
### DNS-Zones ###
#################

module "dns-zones" {
  source              = "./modules/network/dns/zone"
  #depends_on          = [module.dns-views]
  for_each            = { for k, v in var.zones : k => v if var.zones != null }
  zone_compartment_id = length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]
  zone_name           = each.value.display_name
  zone_type           = "PRIMARY"
  zone_defined_tags   = try(each.value.defined_tags, null)
  zone_freeform_tags  = try(each.value.freeform_tags, null)
  zone_scope          = "PRIVATE"
  view_id    = length(regexall("ocid1.dnsview.oc*", each.value.view_id)) > 0 ? each.value.view_id : try(data.oci_dns_views.all_views_data[each.value.view_id].views.*.id[0], module.dns-views[each.value.view_id]["views"].*.id[0])
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
