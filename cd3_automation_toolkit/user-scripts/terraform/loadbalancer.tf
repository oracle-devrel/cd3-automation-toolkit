# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Network
# Create Load Balancers
############################

/*
data "oci_certificates_management_certificates" "certificates_backendsets" {
    for_each = var.backend_sets != null ? var.backend_sets : {}
    #Optional
    compartment_id = each.value.instance_compartment != null ? (length(regexall("ocid1.compartment.oc*", each.value.instance_compartment)) > 0 ? each.value.instance_compartment : var.compartment_ocids[each.value.instance_compartment]) :  var.tenancy_ocid
    name = each.value.certificate_name
    state = "AVAILABLE"
}
*/

data "oci_core_instances" "instances" {
  # depends_on = [module.instances] # Uncomment to create Compute and Load Balancers together
  for_each = var.backends != null ? var.backends : {}
  #state    = "RUNNING"
  filter {
    name   = "state"
    values = ["RUNNING","STOPPED"]
  }
  #Required
  compartment_id = each.value.instance_compartment != null && each.value.instance_compartment != "" ? (length(regexall("ocid1.compartment.oc*", each.value.instance_compartment)) > 0 ? each.value.instance_compartment : var.compartment_ocids[each.value.instance_compartment]) : var.tenancy_ocid
}

data "oci_core_instance" "instance_ip" {
  for_each    = { for k, v in var.backends : k => v.ip_address if length(regexall("IP:*", v.ip_address)) == 0 }
  instance_id = merge(local.instance.ocid.*...)[split("NAME:", each.value)[1]][0]
}

locals {
  instance = {
    for instances in data.oci_core_instances.instances :
    "ocid" => { for instance in instances.instances : instance.display_name => instance.id... }...
  }
}

module "load-balancers" {
  # depends_on = [module.vcns, module.subnets,module.nsgs] # Uncomment to execute Networking and Load Balancer together
  source   = "./modules/loadbalancer/lb-load-balancer"
  for_each = var.load_balancers != null ? var.load_balancers : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_names      = [each.value.vcn_name]

  display_name = each.value.display_name
  shape        = each.value.shape != null ? each.value.shape : "100Mbps" # Default value as per OCI
  #subnet_ids = flatten(tolist([for subnet in each.value.subnet_names : (length(regexall("ocid1.subnet.oc*", subnet)) > 0 ? [subnet] : data.oci_core_subnets.oci_subnets_lbs[subnet].subnets[*].id)]))
  subnet_ids             = each.value.subnet_ids
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null

  #Optional
  defined_tags               = each.value.defined_tags
  freeform_tags              = each.value.freeform_tags
  ip_mode                    = each.value.ip_mode
  is_private                 = each.value.is_private
  network_security_group_ids = each.value.nsg_ids
  key_name                   = each.key
  load_balancers             = var.load_balancers
  reserved_ips_id            = each.value.reserved_ips_id != null ? (lower(each.value.reserved_ips_id) != "n" ? (length(regexall("ocid1.publicip.oc*", each.value.reserved_ips_id)) > 0 ? [each.value.reserved_ips_id] : [merge(module.lbr-reserved-ips.*...)[join("-", [each.key, "reserved", "ip"])].reserved_ip_tf_id]) : []) : []
}

/*
output "load_balancer_id_map" {
  value = [ for k,v in merge(module.load-balancers.*...) : v.load_balancer_tf_id ]
}
*/

module "hostnames" {
  source   = "./modules/loadbalancer/lb-hostname"
  for_each = var.hostnames != null ? var.hostnames : {}

  #Required
  hostname         = each.value.hostname
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name             = each.value.name
}

/*
output "hostnames_id_map" {
	value = [ for k,v in merge(module.hostnames.*...) : v.hostname_tf_id ]
}
*/

module "certificates" {
  source   = "./modules/loadbalancer/lb-certificate"
  for_each = var.certificates != null ? var.certificates : {}

  #Required
  certificate_name = each.value.certificate_name
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]

  #Optional
  ca_certificate     = each.value.ca_certificate != null ? file(each.value.ca_certificate) : null
  passphrase         = each.value.passphrase
  private_key        = each.value.private_key != null ? file(each.value.private_key) : null
  public_certificate = each.value.public_certificate != null ? file(each.value.public_certificate) : null
}

/*
output "certificates_id_map" {
	value = [ for k,v in merge(module.certificates.*...) : v.certificate_tf_id ]
}
*/

module "cipher-suites" {
  source   = "./modules/loadbalancer/lb-cipher-suite"
  for_each = var.cipher_suites != null ? var.cipher_suites : {}

  #Required
  ciphers          = each.value.ciphers
  name             = each.value.name
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]

}

/*
output "cipher_suites_id_map" {
	value = [ for k,v in merge(module.cipher-suites.*...) : v.cipher_suite_tf_id ]
}
*/

module "backend-sets" {
  source   = "./modules/loadbalancer/lb-backend-set"
  for_each = var.backend_sets != null ? var.backend_sets : {}

  #Required
  protocol = each.value.protocol

  #Optional
  interval_ms         = each.value.interval_ms
  is_force_plain_text = each.value.is_force_plain_text
  port                = each.value.port
  response_body_regex = each.value.response_body_regex
  retries             = each.value.retries
  return_code         = each.value.return_code
  timeout_in_millis   = each.value.timeout_in_millis
  url_path            = each.value.url_path

  load_balancer_id  = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name              = each.value.name
  policy            = each.value.policy
  backend_sets      = var.backend_sets
  certificate_name  = each.value.certificate_name != null ? merge(module.certificates.*...)[each.value.certificate_name]["certificate_tf_name"] : null
  cipher_suite_name = each.value.cipher_suite_name != null ? (length(regexall("oci-default-ssl", each.value.cipher_suite_name)) < 0 ? merge(module.cipher-suites.*...)[each.value.cipher_suite_name]["cipher_suite_tf_name"] : "") : null
  key_name          = each.key

}

/*
output "backend_sets_id_map" {
    value = [ for k,v in merge(module.backend-sets.*...) : v.backend_set_tf_id ]
}
*/

module "backends" {
  depends_on = [module.backend-sets]
  source     = "./modules/loadbalancer/lb-backend"
  for_each   = var.backends != null ? var.backends : {}

  #Required
  backendset_name  = merge(module.backend-sets.*...)[each.value.backendset_name].backend_set_tf_name
  ip_address       = each.value.ip_address != "" ? (length(regexall("IP:", each.value.ip_address)) > 0 ? split("IP:", each.value.ip_address)[1] : data.oci_core_instance.instance_ip[each.key].private_ip) : null
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  port             = each.value.port

  #Optional
  backup  = each.value.backup
  drain   = each.value.drain
  offline = each.value.offline
  weight  = each.value.weight != null ? each.value.weight : "1"
}

/*
output "backends_id_map" {
    value = [ for k,v in merge(module.backends.*...) : v.backend_tf_id ]
}
*/

module "listeners" {
  source   = "./modules/loadbalancer/lb-listener"
  for_each = var.listeners != null ? var.listeners : {}

  #Required
  default_backend_set_name = merge(module.backend-sets.*...)[each.value.default_backend_set_name].backend_set_tf_name
  load_balancer_id         = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name                     = each.value.name
  port                     = each.value.port
  protocol                 = each.value.protocol

  #Optional
  listeners           = var.listeners
  certificate_name    = each.value.certificate_name != null ? merge(module.certificates.*...)[each.value.certificate_name]["certificate_tf_name"] : null
  cipher_suite_name   = each.value.cipher_suite_name != null ? (length(regexall("oci-default-ssl", each.value.cipher_suite_name)) < 0 ? each.value.cipher_suite_name : null) : null
  key_name            = each.key
  hostname_names      = each.value.hostname_names != null ? flatten(tolist([for hostnames in each.value.hostname_names : merge(module.hostnames.*...)[hostnames].hostname_tf_name])) : null
  path_route_set_name = each.value.path_route_set_name != null ? merge(module.path-route-sets.*...)[each.value.path_route_set_name].path_route_set_tf_name : null
  routing_policy_name = each.value.routing_policy_name #TODO
  rule_set_names      = each.value.rule_set_names != null ? flatten(tolist([for rules in each.value.rule_set_names : merge(module.rule-sets.*...)[rules].rule_set_tf_name])) : null
}

/*
output "listeners_id_map" {
    value = [ for k,v in merge(module.listeners.*...) : v.listener_tf_id ]
}
*/

module "path-route-sets" {
  depends_on = [module.backend-sets]
  source     = "./modules/loadbalancer/lb-path-route-set"
  for_each   = var.path_route_sets != null ? var.path_route_sets : {}

  #Required
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name             = each.value.name

  #Optional
  path_route_sets = var.path_route_sets
  key_name        = each.key
}

/*
output "path_route_sets_id_map" {
    value = [ for k,v in merge(module.path-route-sets.*...) : v.path_route_set_tf_id ]
}
*/

module "rule-sets" {
  source   = "./modules/loadbalancer/lb-rule-set"
  for_each = var.rule_sets != null ? var.rule_sets : {}

  #Required
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name             = each.value.name

  #Optional
  rule_sets = var.rule_sets
  key_name  = each.key
}

/*
output "rule_sets_id_map" {
    value = [ for k,v in merge(module.rule-sets.*...) : v.rule_set_tf_id ]
}
*/

module "routing-policies" {
  source   = "./modules/loadbalancer/lb-routing-policy"
  for_each = var.lb_routing_policies != null ? var.lb_routing_policies : {}

  condition_language_version = each.value.condition_language_version != null ? each.value.condition_language_version : null
  load_balancer_id           = length(regexall("ocid1.loadbalancer.oc*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name                       = each.value.name != null ? each.value.name : null
  #backend_set_name           = each.value.backend_set_name != null ? merge(module.backend-sets.*...)[each.value.backend_set_name].backend_set_tf_name : null
  rules = each.value.rules != null ? each.value.rules : []

}

/*
output "routing_policy_tf_id_map" {
    value = [ for k,v in merge(module.routing-policies.*...) : v.routing_policy_tf_id ]
}
*/

#############################
# Module Block - LBaaS Logging
# Create Log Groups and Logs
#############################

module "loadbalancer-log-groups" {
  source   = "./modules/managementservices/log-group"
  for_each = (var.loadbalancer_log_groups != null || var.loadbalancer_log_groups != {}) ? var.loadbalancer_log_groups : {}

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
output "log_group_map" {
  value = [ for k,v in merge(module.loadbalancer-log-groups.*...) : v.log_group_tf_id ]
}
*/

module "loadbalancer-logs" {
  source   = "./modules/managementservices/log"
  for_each = (var.loadbalancer_logs != null || var.loadbalancer_logs != {}) ? var.loadbalancer_logs : {}

  # Logs
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.display_name
  log_group_id   = length(regexall("ocid1.loggroup.oc*", each.value.log_group_id)) > 0 ? each.value.log_group_id : merge(module.loadbalancer-log-groups.*...)[each.value.log_group_id]["log_group_tf_id"]

  log_type = each.value.log_type
  #Required
  source_category        = each.value.category
  source_resource        = length(regexall("ocid1.*", each.value.resource)) > 0 ? each.value.resource : merge(module.load-balancers.*...)[each.value.resource]["load_balancer_tf_id"]
  source_service         = each.value.service
  source_type            = each.value.source_type
  defined_tags           = each.value.defined_tags
  freeform_tags          = each.value.freeform_tags
  log_is_enabled         = (each.value.is_enabled == "" || each.value.is_enabled == null) ? true : each.value.is_enabled
  log_retention_duration = (each.value.retention_duration == "" || each.value.retention_duration == null) ? 30 : each.value.retention_duration

}

/*
output "logs_id" {
  value = [ for k,v in merge(module.loadbalancer-logs.*...) : v.log_tf_id]
}
*/

# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Block - Reserved IPs for LBaaS
# Create Reserved IPs for LBaaS
# Allowed Values:
# Lifetime Values can be one of EPHEMERAL or RESERVED
############################################

module "lbr-reserved-ips" {
  source   = "./modules/ip/reserved-public-ip"
  for_each = var.lbr_reserved_ips != null && var.lbr_reserved_ips != {} ? var.lbr_reserved_ips : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  lifetime       = each.value.lifetime

  #Optional
  defined_tags  = each.value.defined_tags
  display_name  = each.value.display_name
  freeform_tags = each.value.freeform_tags
  private_ip_id = each.value.private_ip_id
  #private_ip_id        = each.value.private_ip_id != null ? (length(regexall("ocid1.privateip.oc*", each.value.private_ip_id)) > 0 ? each.value.private_ip_id : (length(regexall("\\.", each.value.private_ip_id)) == 3 ? local.private_ip_id[0][each.value.private_ip_id] : merge(module.private-ips.*...)[each.value.private_ip_id].private_ip_tf_id)) : null
  #public_ip_pool_id    = each.value.public_ip_pool_id != null ? (length(regexall("ocid1.publicippool.oc*", each.value.public_ip_pool_id)) > 0 ? each.value.public_ip_pool_id : merge(module.public-ip-pools.*...)[each.value.public_ip_pool_id].public_ip_pool_tf_id) : null
}
