// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Module Block - Network Load Balancer
# Create Network Load Balancer
#######################################

data "oci_core_subnets" "oci_nlb_subnets" {
  for_each = var.network_load_balancers != null ? var.network_load_balancers : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
}

data "oci_core_instances" "nlb_instances" {
    for_each = var.nlb_backends != null ? var.nlb_backends : {}
    #Required
    compartment_id = each.value.instance_compartment != null ? (length(regexall("ocid1.compartment.oc1*", each.value.instance_compartment)) > 0 ? each.value.instance_compartment : var.compartment_ocids[each.value.instance_compartment]) :  var.tenancy_ocid
}

data "oci_core_instance" "nlb_instance_ip" {
    for_each = { for k,v in var.nlb_backends : k => v.ip_address if length(regexall("IP:*", v.ip_address)) == 0 }
    instance_id = flatten(distinct(local.nlb_instance.ocid))[0][split("NAME:", each.value)[1]][0]
}

locals {
    nlb_instance = {
        for instances in data.oci_core_instances.nlb_instances:
           "ocid" => { for instance in instances.instances : instance.display_name => instance.id... }...
    }
}

module network-load-balancers {
  source = "./modules/networkloadbalancer/nlb"
  for_each = var.network_load_balancers != null ? var.network_load_balancers : {}
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null 
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name = each.value.display_name
  subnet_id = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc1*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_nlb_subnets[each.key].subnets.*.id[0]) : null
  is_preserve_source_destination = each.value.is_preserve_source_destination != null ? each.value.is_preserve_source_destination : null
  #is_private = each.value.is_private != null ? each.value.is_private : null
  network_security_group_ids = each.value.nsg_ids != null ? each.value.nsg_ids : null
  nlb_ip_version = each.value.nlb_ip_version != null ? each.value.nlb_ip_version : null
  vcn_name = each.value.vcn_name
  defined_tags = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  reserved_ips_id = lower(each.value.reserved_ips_id) != "n" && each.value.reserved_ips_id != "" ? (length(regexall("ocid1.publicip.oc1*", each.value.reserved_ips_id)) > 0 ? [each.value.reserved_ips_id] : [merge(module.nlb-reserved-ips.*...)[join("-",[each.key,"reserved","ip"])].reserved_ip_tf_id]) : []

}

module nlb-listeners {
  source = "./modules/networkloadbalancer/nlb-listener"
  for_each = var.nlb_listeners != null ? var.nlb_listeners : {}
  name = each.value.name
  default_backend_set_name = merge(module.nlb-backend-sets.*...)[each.value.default_backend_set_name].nlb_backend_set_tf_name
  network_load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.network_load_balancer_id)) > 0 ? each.value.network_load_balancer_id : merge(module.network-load-balancers.*...)[each.value.network_load_balancer_id]["network_load_balancer_tf_id"]
  port = each.value.port
  protocol = each.value.protocol
  ip_version = each.value.ip_version
}

module nlb-backend-sets {
  source = "./modules/networkloadbalancer/nlb-backendset"
  for_each = var.nlb_backend_sets != null ? var.nlb_backend_sets : {}
  name = each.value.name
  network_load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.network_load_balancer_id)) > 0 ? each.value.network_load_balancer_id : merge(module.network-load-balancers.*...)[each.value.network_load_balancer_id]["network_load_balancer_tf_id"]
  policy = each.value.policy
  ip_version = each.value.ip_version != null ? each.value.ip_version : null
  is_preserve_source = each.value.is_preserve_source != null ? each.value.is_preserve_source : null
  #healthcheck parameters
  protocol = each.value.protocol
  interval_in_millis = each.value.interval_in_millis  != null ? each.value.interval_in_millis : null
  port = each.value.port  != null ? each.value.port : null
  response_body_regex = each.value.response_body_regex  != null ? each.value.response_body_regex : null
  retries = each.value.retries != null ? each.value.retries : null
  return_code = each.value.return_code  != null ? each.value.return_code : null
  timeout_in_millis = each.value.timeout_in_millis  != null ? each.value.timeout_in_millis : null
  url_path = each.value.url_path != null ? each.value.url_path : null
}

module nlb-backends {
  source = "./modules/networkloadbalancer/nlb-backend"
  for_each = var.nlb_backends != null ? var.nlb_backends : {}
  backend_set_name = merge(module.nlb-backend-sets.*...)[each.value.backend_set_name]["nlb_backend_set_tf_name"]
  network_load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.network_load_balancer_id)) > 0 ? each.value.network_load_balancer_id : merge(module.network-load-balancers.*...)[each.value.network_load_balancer_id]["network_load_balancer_tf_id"]
  port = each.value.port
  ip_address = each.value.ip_address != "" ? (length(regexall("IP:", each.value.ip_address)) > 0 ? split("IP:", each.value.ip_address)[1] : data.oci_core_instance.nlb_instance_ip[each.key].private_ip) : null
  #ip_address = each.value.ip_address != "" ? (length(regexall("IP:", each.value.ip_address)) > 0 ? split("IP:", each.value.ip_address)[1] : data.oci_core_instance.nlb_instance_ip[each.key].private_ip) : (length(regexall("NAME:", each.value.ip_address)) > 0 ? split("NAME:", each.value.ip_address)[1] : data.oci_core_instance.nlb_instance[each.key].private_ip) : null
  
  
  is_backup = each.value.is_backup != "" ? each.value.is_backup : "false"
  is_drain = each.value.is_drain != "" ? each.value.is_drain : "false"
  is_offline = each.value.is_offline != "" ? each.value.is_offline : "false"
  name = each.value.name != "" ? each.value.name : ""
  #target_id = each.value.target_id != "" ? each.value.target_id : ""
  target_id = data.oci_core_instance.nlb_instance_ip[each.key].id
  
  weight = each.value.weight != "" ? each.value.weight : "1"
}
############################################
# Module Block - Reserved IPs for NLBs
# Create Reserved IPs for NLBs
# Allowed Values:
# Lifetime Values can be one of EPHEMERAL or RESERVED
############################################

module "nlb-reserved-ips" {
    source = "./modules/ip/reserved-public-ip"
    for_each = var.nlb_reserved_ips != null && var.nlb_reserved_ips != {}  ? var.nlb_reserved_ips : {}

    #Required
    compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
    lifetime = each.value.lifetime

    #Optional
    defined_tags         = each.value.defined_tags
    display_name         = each.value.display_name
    freeform_tags        = each.value.freeform_tags
    #private_ip_id        = each.value.private_ip_id != "" ? (length(regexall("ocid1.privateip.oc1*", each.value.private_ip_id)) > 0 ? each.value.private_ip_id : (length(regexall("\\.", each.value.private_ip_id)) == 3 ? local.private_ip_id[0][each.value.private_ip_id] : merge(module.private-ips.*...)[each.value.private_ip_id].private_ip_tf_id)) : null
    #public_ip_pool_id    = each.value.public_ip_pool_id != "" ? (length(regexall("ocid1.publicippool.oc1*", each.value.public_ip_pool_id)) > 0 ? each.value.public_ip_pool_id : merge(module.public-ip-pools.*...)[each.value.public_ip_pool_id].public_ip_pool_tf_id) : null
}

