# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Module Block - Network Load Balancer
# Create Network Load Balancer
#######################################

data "oci_core_subnets" "oci_subnets_nlb" {
  # depends_on = [module.subnets] # Uncomment to create Network and NLBs together
  for_each       = var.network_load_balancers != null ? var.network_load_balancers : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_nlb[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_nlb" {
  # depends_on = [module.vcns] # Uncomment to create Network and NLBs together
  for_each       = var.network_load_balancers != null ? var.network_load_balancers : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "network-load-balancers" {
  # depends_on = [module.nsgs] # Uncomment to create NSG and NLBs together
  source                         = "./modules/networkloadbalancer/nlb"
  for_each                       = var.network_load_balancers != null ? var.network_load_balancers : {}
  network_compartment_id         = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  compartment_id                 = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name                   = each.value.display_name
  subnet_id                      = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_nlb[each.key].subnets.*.id[0]) : null
  is_preserve_source_destination = each.value.is_preserve_source_destination
  is_symmetric_hash_enabled      = each.value.is_symmetric_hash_enabled
  is_private                     = each.value.is_private
  network_security_group_ids     = each.value.nsg_ids
  nlb_ip_version                 = each.value.nlb_ip_version
  assigned_private_ipv4          = each.value.assigned_private_ipv4
  vcn_name                       = each.value.vcn_name
  defined_tags                   = each.value.defined_tags
  freeform_tags                  = each.value.freeform_tags
  reserved_ips_id                = each.value.reserved_ips_id != "" && lower(each.value.reserved_ips_id) != "n" ? (length(regexall("ocid1.publicip.oc*", each.value.reserved_ips_id)) > 0 ? [each.value.reserved_ips_id] : [merge(module.nlb-reserved-ips.*...)[join("-", [each.key, "reserved", "ip"])].reserved_ip_tf_id]) : []
}

module "nlb-listeners" {
  source                   = "./modules/networkloadbalancer/nlb-listener"
  for_each                 = var.nlb_listeners != null ? var.nlb_listeners : {}
  name                     = each.value.name
  default_backend_set_name = merge(module.nlb-backend-sets.*...)[each.value.default_backend_set_name].nlb_backend_set_tf_name
  network_load_balancer_id = length(regexall("ocid1.networkloadbalancer.oc*", each.value.network_load_balancer_id)) > 0 ? each.value.network_load_balancer_id : merge(module.network-load-balancers.*...)[each.value.network_load_balancer_id]["network_load_balancer_tf_id"]
  port                     = each.value.port
  protocol                 = each.value.protocol
  ip_version               = each.value.ip_version
}

module "nlb-backend-sets" {
  source                   = "./modules/networkloadbalancer/nlb-backendset"
  for_each                 = var.nlb_backend_sets != null ? var.nlb_backend_sets : {}
  name                     = each.value.name
  network_load_balancer_id = length(regexall("ocid1.networkloadbalancer.oc*", each.value.network_load_balancer_id)) > 0 ? each.value.network_load_balancer_id : merge(module.network-load-balancers.*...)[each.value.network_load_balancer_id]["network_load_balancer_tf_id"]
  policy                   = each.value.policy
  ip_version               = each.value.ip_version
  is_preserve_source       = each.value.is_preserve_source
  #healthcheck parameters
  domain_name        = each.value.domain_name
  query_class        = each.value.query_class
  query_type         = each.value.query_type
  rcodes             = each.value.rcodes
  transport_protocol = each.value.transport_protocol

  protocol            = each.value.protocol
  interval_in_millis  = each.value.interval_in_millis
  port                = each.value.port
  request_data        = each.value.request_data
  response_body_regex = each.value.response_body_regex
  response_data       = each.value.response_data
  retries             = each.value.retries
  return_code         = each.value.return_code
  timeout_in_millis   = each.value.timeout_in_millis
  url_path            = each.value.url_path
}

module "nlb-backends" {
  source = "./modules/networkloadbalancer/nlb-backend"
  # depends_on = [module.instances] # Uncomment to create Network and NLBs together
  for_each                 = var.nlb_backends != null ? var.nlb_backends : {}
  backend_set_name         = merge(module.nlb-backend-sets.*...)[each.value.backend_set_name]["nlb_backend_set_tf_name"]
  network_load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.network_load_balancer_id)) > 0 ? each.value.network_load_balancer_id : merge(module.network-load-balancers.*...)[each.value.network_load_balancer_id]["network_load_balancer_tf_id"]
  port                     = each.value.port
  #vnic_vlan                = each.value.vnic_vlan != null ? each.value.vnic_vlan : null
  ip_address               = each.value.ip_address
  instance_compartment     = each.value.instance_compartment != "" ? (length(regexall("ocid1.compartment.oc*", each.value.instance_compartment)) > 0 ? each.value.instance_compartment : var.compartment_ocids[each.value.instance_compartment]) : var.tenancy_ocid
  #ip_address = each.value.ip_address != "" ? (length(regexall("IP:", each.value.ip_address)) > 0 ? split("IP:", each.value.ip_address)[1] : data.oci_core_instance.nlb_instance_ip[each.key].private_ip) : (length(regexall("NAME:", each.value.ip_address)) > 0 ? split("NAME:", each.value.ip_address)[1] : data.oci_core_instance.nlb_instance[each.key].private_ip) : null


  is_drain   = each.value.is_drain != "" ? each.value.is_drain : "false"
  is_backup  = each.value.is_backup != "" ? each.value.is_backup : "false"
  is_offline = each.value.is_offline != "" ? each.value.is_offline : "false"
  weight     = each.value.weight != "" ? each.value.weight : "1"

  name      = each.value.ip_address
  target_id = each.value.ip_address

}

############################################
# Module Block - Reserved IPs for NLBs
# Create Reserved IPs for NLBs
# Allowed Values:
# Lifetime Values can be one of EPHEMERAL or RESERVED
############################################

module "nlb-reserved-ips" {
  source   = "./modules/ip/reserved-public-ip"
  for_each = var.nlb_reserved_ips != null && var.nlb_reserved_ips != {} ? var.nlb_reserved_ips : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  lifetime       = each.value.lifetime

  #Optional
  defined_tags  = each.value.defined_tags
  display_name  = each.value.display_name
  freeform_tags = each.value.freeform_tags
  #private_ip_id        = each.value.private_ip_id != "" ? (length(regexall("ocid1.privateip.oc*", each.value.private_ip_id)) > 0 ? each.value.private_ip_id : (length(regexall("\\.", each.value.private_ip_id)) == 3 ? local.private_ip_id[0][each.value.private_ip_id] : merge(module.private-ips.*...)[each.value.private_ip_id].private_ip_tf_id)) : null
  #public_ip_pool_id    = each.value.public_ip_pool_id != "" ? (length(regexall("ocid1.publicippool.oc*", each.value.public_ip_pool_id)) > 0 ? each.value.public_ip_pool_id : merge(module.public-ip-pools.*...)[each.value.public_ip_pool_id].public_ip_pool_tf_id) : null
}

