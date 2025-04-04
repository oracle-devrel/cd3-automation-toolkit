# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
data "oci_core_vcns" "firewall_vcns" {
  for_each       = var.firewalls != null ? var.firewalls : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}
data "oci_core_subnets" "firewall_subnets" {
  for_each       = var.firewalls != null ? var.firewalls : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.firewall_vcns[each.key].virtual_networks.*.id[0]
}

module "firewalls" {
  source                     = "./modules/security/firewall/firewall"
  for_each                   = var.firewalls != null ? var.firewalls : {}
  depends_on                 = [module.policies, module.address_lists, module.application_groups, module.applications, module.services, module.service_lists, module.url_lists, module.decryption_profiles, module.secrets, module.security_rules, module.decryption_rules]
  compartment_id             = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.compartment_ocids[each.value.compartment_id]
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  subnet_id                  = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.firewall_subnets[each.key].subnets.*.id[0]) : null
  display_name               = each.value.display_name
  ipv4address                = each.value.ipv4address
  ipv6address                = each.value.ipv6address
  availability_domain        = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  nsg_id                     = each.value.nsg_id
  vcn_name                   = each.value.vcn_name
  defined_tags               = each.value.defined_tags
  freeform_tags              = each.value.freeform_tags

}

module "policies" {
  source         = "./modules/security/firewall/firewall-policy"
  for_each       = var.fw-policies != null ? var.fw-policies : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.compartment_ocids[each.value.compartment_id]
  display_name   = each.value.display_name
  defined_tags   = each.value.defined_tags
  freeform_tags  = each.value.freeform_tags
}

module "services" {
  source                     = "./modules/security/firewall/service"
  for_each                   = var.services != null ? var.services : {}
  depends_on                 = [module.policies]
  service_name               = each.value.service_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  service_type               = each.value.service_type
  port_ranges                = each.value.port_ranges
}

module "service_lists" {
  source                     = "./modules/security/firewall/service-list"
  for_each                   = var.service_lists != null ? var.service_lists : {}
  depends_on                 = [module.services, module.policies]
  service_list_name          = each.value.service_list_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  services                   = each.value.services != null ? flatten(tolist([for sid in each.value.services : (length(regexall("ocid1.networkfirewallpolicy.oc*", sid)) > 0 ? merge(module.services.*...)[sid]["service+_tf_id"] : [sid])])) : null
}

module "address_lists" {
  source                     = "./modules/security/firewall/address-list"
  for_each                   = var.address_lists != null ? var.address_lists : {}
  depends_on                 = [module.policies]
  address_list_name          = each.value.address_list_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  address_type               = each.value.address_type
  addresses                  = each.value.addresses
}

module "applications" {
  source                     = "./modules/security/firewall/application"
  for_each                   = var.applications != null ? var.applications : {}
  depends_on                 = [module.policies]
  icmp_type                  = each.value.icmp_type
  app_list_name              = each.value.app_list_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  app_type                   = each.value.app_type
  icmp_code                  = each.value.icmp_code
}

module "application_groups" {
  source                     = "./modules/security/firewall/application-group"
  for_each                   = var.application_groups != null ? var.application_groups : {}
  depends_on                 = [module.policies, module.applications]
  app_group_name             = each.value.app_group_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  apps                       = each.value.apps != null ? flatten(tolist([for app in each.value.apps : (length(regexall("ocid1.networkfirewallpolicy.oc*", app)) > 0 ? merge(module.applications.*...)[app]["application_tf_id"] : [app])])) : null
}

module "url_lists" {
  source                     = "./modules/security/firewall/url-list"
  for_each                   = var.url_lists != null ? var.url_lists : {}
  depends_on                 = [module.policies]
  urllist_name               = each.value.urllist_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  #key_name  = each.key
  urls_details = each.value.urls
}

module "security_rules" {
  source                     = "./modules/security/firewall/security-rules"
  for_each                   = var.security_rules != null ? var.security_rules : {}
  depends_on                 = [module.policies, module.address_lists, module.application_groups, module.applications, module.services, module.service_lists, module.url_lists]
  action                     = each.value.action
  rule_name                  = each.value.rule_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  application                = each.value.condition[0].application != null ? each.value.condition[0].application : []
  url                        = each.value.condition[0].url != null ? each.value.condition[0].url : []
  service                    = each.value.condition[0].service != null ? each.value.condition[0].service : []
  source_address             = each.value.condition[0].source_address != null ? each.value.condition[0].source_address : []
  destination_address        = each.value.condition[0].destination_address != null ? each.value.condition[0].destination_address : []
  /*application = each.value.condition != null ? each.value.condition.application : []
  url = each.value.condition != null ? each.value.condition.url  : []
  service = each.value.condition != null ? each.value.condition.service : []
  source_address = each.value.condition != null ? each.value.condition.source_address : []
  destination_address = each.value.condition != null ? each.value.condition.destination_address : []*/
  inspection  = each.value.inspection
  after_rule  = each.value.after_rule
  before_rule = each.value.before_rule
}

module "secrets" {
  source                     = "./modules/security/firewall/secret"
  for_each                   = var.secrets != null || var.secrets != {} ? var.secrets : {}
  depends_on                 = [module.policies]
  secret_name                = each.value.secret_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  secret_source              = each.value.secret_source
  secret_type                = each.value.secret_type
  vault_secret_id            = each.value.vault_secret_id
  vault_name                 = each.value.vault_name
  compartment_id             = each.value.vault_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.vault_compartment_id)) > 0 ? each.value.vault_compartment_id : var.compartment_ocids[each.value.vault_compartment_id]) : var.compartment_ocids[each.value.vault_compartment_id]
  version_number             = each.value.version_number
}

module "decryption_profiles" {
  source                                = "./modules/security/firewall/decryption-profile"
  for_each                              = var.decryption_profiles != null || var.decryption_profiles != {} ? var.decryption_profiles : {}
  depends_on                            = [module.policies, module.secrets]
  profile_name                          = each.value.profile_name
  network_firewall_policy_id            = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  profile_type                          = each.value.profile_type
  are_certificate_extensions_restricted = each.value.are_certificate_extensions_restricted
  is_auto_include_alt_name              = each.value.is_auto_include_alt_name
  is_expired_certificate_blocked        = each.value.is_expired_certificate_blocked
  is_out_of_capacity_blocked            = each.value.is_out_of_capacity_blocked
  is_revocation_status_timeout_blocked  = each.value.is_revocation_status_timeout_blocked
  is_unknown_revocation_status_blocked  = each.value.is_unknown_revocation_status_blocked
  is_unsupported_cipher_blocked         = each.value.is_unsupported_cipher_blocked
  is_unsupported_version_blocked        = each.value.is_unsupported_version_blocked
  is_untrusted_issuer_blocked           = each.value.is_untrusted_issuer_blocked
}

module "decryption_rules" {
  source                     = "./modules/security/firewall/decryption-rules"
  for_each                   = var.decryption_rules != null ? var.decryption_rules : {}
  depends_on                 = [module.policies, module.decryption_profiles, module.secrets, module.address_lists]
  action                     = each.value.action
  rule_name                  = each.value.rule_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  source_address             = each.value.condition[0].source_address != null ? each.value.condition[0].source_address : []
  destination_address        = each.value.condition[0].destination_address != null ? each.value.condition[0].destination_address : []
  after_rule                 = each.value.after_rule
  before_rule                = each.value.before_rule
  decryption_profile         = each.value.decryption_profile
  secret                     = each.value.secret
}

module "tunnelinspect_rules" {
  source                     = "./modules/security/firewall/tunnel-inspect"
  for_each                   = var.tunnelinspect_rules != null ? var.tunnelinspect_rules : {}
  depends_on                 = [module.policies, module.address_lists]
  action                     = each.value.action
  rule_name                  = each.value.rule_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policies.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  source_address             = each.value.condition[0].source_address != null ? each.value.condition[0].source_address : []
  destination_address        = each.value.condition[0].destination_address != null ? each.value.condition[0].destination_address : []
  after_rule                 = each.value.after_rule
  before_rule                = each.value.before_rule
  protocol        = each.value.protocol
}


#############################
# Module Block - Network Firewall Logging
# Create VCN Log Groups and Logs
#############################

module "fw-log-groups" {
  source   = "./modules/managementservices/log-group"
  for_each = (var.fw_log_groups != null || var.fw_log_groups != {}) ? var.fw_log_groups : {}

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

module "fw-logs" {
  source   = "./modules/managementservices/log"
  for_each = (var.fw_logs != null || var.fw_logs != {}) ? var.fw_logs : {}

  # Logs
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.display_name
  log_group_id   = length(regexall("ocid1.loggroup.oc*", each.value.log_group_id)) > 0 ? each.value.log_group_id : merge(module.fw-log-groups.*...)[each.value.log_group_id]["log_group_tf_id"]

  log_type = each.value.log_type
  #Required
  source_category        = each.value.category
  source_resource        = length(regexall("ocid1.*", each.value.resource)) > 0 ? each.value.resource : merge(module.firewalls.*...)[each.value.resource]["firewall_tf_id"]
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