############################
# Module Block - Network
# Create Load Balancers
############################

data "oci_core_instances" "instances" {
    for_each = var.backends != null ? var.backends : {}
    #Required
    compartment_id = each.value.instance_compartment != null ? (length(regexall("ocid1.compartment.oc1*", each.value.instance_compartment)) > 0 ? each.value.instance_compartment : var.compartment_ocids[each.value.instance_compartment]) :  var.tenancy_ocid
}

data "oci_core_instance" "instance_ip" {
    for_each = { for k,v in var.backends : k => v.ip_address if length(regexall("IP:*", v.ip_address)) == 0 }
    instance_id = flatten(distinct(local.instance.ocid))[0][split("NAME:", each.value)[1]][0]
}

locals {
    instance = {
        for instances in data.oci_core_instances.instances:
           "ocid" => { for instance in instances.instances : instance.display_name => instance.id... }...
    }
}

module "load-balancers" {
  source   = "./modules/loadbalancer/lb-load-balancer"
  for_each = var.load_balancers != null ? var.load_balancers : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vcn_names      = [each.value.vcn_name]

  display_name = each.value.display_name
  shape        = each.value.shape != "" ? each.value.shape : "100Mbps" # Default value as per OCI
  #subnet_ids = flatten(tolist([for subnet in each.value.subnet_names : (length(regexall("ocid1.subnet.oc1*", subnet)) > 0 ? [subnet] : data.oci_core_subnets.oci_subnets_lbs[subnet].subnets[*].id)]))
  subnet_ids             = each.value.subnet_names
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null

  #Optional
  defined_tags               = each.value.defined_tags
  freeform_tags              = each.value.freeform_tags
  ip_mode                    = each.value.ip_mode != "" ? each.value.ip_mode : "IPV4"
  is_private                 = each.value.is_private != "" ? each.value.is_private : "false"
  network_security_group_ids = each.value.nsg_ids
  key_name                   = each.key
  load_balancers             = var.load_balancers
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
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
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
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]

  #Optional
  ca_certificate     = each.value.ca_certificate != "" ? file(each.value.ca_certificate) : null
  passphrase         = each.value.passphrase != "" ? each.value.passphrase : null
  private_key        = each.value.private_key != "" ? file(each.value.private_key) : null
  public_certificate = each.value.public_certificate != "" ? file(each.value.public_certificate) : null
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
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]

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
  interval_ms         = each.value.interval_ms != "" ? each.value.interval_ms : null
  port                = each.value.port
  response_body_regex = each.value.response_body_regex
  retries             = each.value.retries != "" ? each.value.retries : null
  return_code         = each.value.return_code != "" ? each.value.return_code : null
  timeout_in_millis   = each.value.return_code != "" ? each.value.timeout_in_millis : null
  url_path            = each.value.url_path != "" ? each.value.url_path : null

  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name             = each.value.name
  policy           = each.value.policy
  backend_sets     = var.backend_sets
  certificate_name = each.value.certificate_name != "" ? merge(module.certificates.*...)[each.value.certificate_name]["certificate_tf_name"] : ""
  cipher_suite_name = each.value.cipher_suite_name != "" ? merge(module.cipher-suites.*...)[each.value.cipher_suite_name]["cipher_suite_tf_name"] : ""
  key_name         = each.key

}

/*
output "backend_sets_id_map" {
    value = [ for k,v in merge(module.backend-sets.*...) : v.backend_set_tf_id ]
}
*/

module "backends" {
  source   = "./modules/loadbalancer/lb-backend"
  for_each = var.backends != null ? var.backends : {}

  #Required
  backendset_name  = merge(module.backend-sets.*...)[each.value.backendset_name].backend_set_tf_name
  ip_address       = each.value.ip_address != "" ? (length(regexall("IP:", each.value.ip_address)) > 0 ? split("IP:", each.value.ip_address)[1] : data.oci_core_instance.instance_ip[each.key].private_ip) : null
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  port             = each.value.port

  #Optional
  backup  = each.value.backup != "" ? each.value.backup : "false"
  drain   = each.value.drain != "" ? each.value.drain : "false"
  offline = each.value.offline != "" ? each.value.offline : "false"
  weight  = each.value.weight != "" ? each.value.weight : "1"
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
  load_balancer_id         = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
  name                     = each.value.name
  port                     = each.value.port
  protocol                 = each.value.protocol

  #Optional
  listeners           = var.listeners
  certificate_name    = each.value.certificate_name != "" ? merge(module.certificates.*...)[each.value.certificate_name]["certificate_tf_name"] : ""
  cipher_suite_name   = each.value.cipher_suite_name
  key_name            = each.key
  hostname_names      = each.value.hostname_names != [] ? flatten(tolist([for hostnames in each.value.hostname_names : merge(module.hostnames.*...)[hostnames].hostname_tf_name])) : null
  path_route_set_name = each.value.path_route_set_name != "" ? merge(module.path-route-sets.*...)[each.value.path_route_set_name].path_route_set_tf_name : ""
  routing_policy_name = each.value.routing_policy_name #TODO
  rule_set_names      = each.value.rule_set_names != [] ? flatten(tolist([for rules in each.value.rule_set_names : merge(module.rule-sets.*...)[rules].rule_set_tf_name])) : null
}

/*
output "listeners_id_map" {
    value = [ for k,v in merge(module.listeners.*...) : v.listener_tf_id ]
}
*/

module "path-route-sets" {
  source   = "./modules/loadbalancer/lb-path-route-set"
  for_each = var.path_route_sets != null ? var.path_route_sets : {}

  #Required
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
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
  load_balancer_id = length(regexall("ocid1.loadbalancer.oc1*", each.value.load_balancer_id)) > 0 ? each.value.load_balancer_id : merge(module.load-balancers.*...)[each.value.load_balancer_id]["load_balancer_tf_id"]
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