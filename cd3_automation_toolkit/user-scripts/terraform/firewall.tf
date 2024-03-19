data "oci_core_vcns" "firewall_vcn" {
  for_each = var.firewall != null ? var.firewall : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name = each.value.vcn_name
}
data "oci_core_subnets" "firewall_subnets" {
  for_each = var.firewall != null ? var.firewall : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name = each.value.subnet_id
  vcn_id = data.oci_core_vcns.firewall_vcn[each.key].virtual_networks.*.id[0]
}

module "firewall" {
  source = "./modules/security/firewall/firewall"
  for_each = var.firewall != null ? var.firewall :{}
  depends_on = [module.policy,module.address_list, module.application_group, module.application, module.service, module.service_list, module.url_list,module.decryption_profile, module.secret,module.security_rules,module.decryption_rules]
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.compartment_ocids[each.value.compartment_id]
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  subnet_id = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc1*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.firewall_subnets[each.key].subnets.*.id[0]) : null
  display_name = each.value.display_name
  ipv4address = each.value.ipv4address
  ipv6address = each.value.ipv6address
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  nsg_id = each.value.nsg_id
  vcn_name = each.value.vcn_name
  defined_tags          = each.value.defined_tags
  freeform_tags         = each.value.freeform_tags

}

module "policy" {
  source = "./modules/security/firewall/firewall-policy"
  for_each = var.policy != null ? var.policy :{}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.compartment_ocids[each.value.compartment_id]
  display_name   = each.value.display_name
  defined_tags          = each.value.defined_tags
  freeform_tags         = each.value.freeform_tags
  }

module "service" {
  source = "./modules/security/firewall/service"
  for_each = var.service != null ? var.service :{}
  depends_on = [module.policy]
  service_name = each.value.service_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  service_type = each.value.service_type
  port_ranges = each.value.port_ranges
}

module "service_list" {
  source                     = "./modules/security/firewall/service-list"
  for_each                   = var.service_list != null ? var.service_list : {}
  depends_on                 = [module.service,module.policy]
  service_list_name          = each.value.service_list_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  services                   = each.value.services != null ? flatten(tolist([for  sid in each.value.services : (length(regexall("ocid1.networkfirewallpolicy.oc1*", sid)) > 0 ? merge(module.service.*...)[sid]["service+_tf_id"] :[sid] )]))  : null
}

module address_list {
  source                     = "./modules/security/firewall/address-list"
  for_each                   = var.address_list != null ? var.address_list : {}
  depends_on = [module.policy]
  address_list_name = each.value.address_list_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  address_type = each.value.address_type
  addresses = each.value.addresses
}

module application {
  source                     = "./modules/security/firewall/application"
  for_each                   = var.application_list != null ? var.application_list : {}
  depends_on = [module.policy]
  icmp_type = each.value.icmp_type
  app_list_name = each.value.app_list_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  app_type = each.value.app_type
  icmp_code = each.value.icmp_code
}

module application_group {
  source                     = "./modules/security/firewall/application-group"
  for_each                   = var.application_group != null ? var.application_group : {}
  depends_on = [module.policy,module.application]
  app_group_name = each.value.app_group_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*", each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  apps = each.value.apps != null ? flatten(tolist([for  app in each.value.apps : (length(regexall("ocid1.networkfirewallpolicy.oc1*", app)) > 0 ? merge(module.application.*...)[app]["application_tf_id"] :[app] )]))  : null
}

module url_list {
  source                     = "./modules/security/firewall/url-list"
  for_each                   = var.url_list != null ? var.url_list : {}
  depends_on = [module.policy]
  urllist_name = each.value.urllist_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  #key_name  = each.key
  urls_details = each.value.urls
}

module security_rules {
  source                     = "./modules/security/firewall/security-rules"
  for_each                   = var.security_rules != null ? var.security_rules : {}
  depends_on = [module.policy, module.address_list, module.application_group, module.application, module.service, module.service_list, module.url_list]
  action = each.value.action
  rule_name = each.value.rule_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  application = each.value.condition[0].application != null ? each.value.condition[0].application : []
  url = each.value.condition[0].url != null ? each.value.condition[0].url  : []
  service = each.value.condition[0].service != null ? each.value.condition[0].service : []
  source_address = each.value.condition[0].source_address != null ? each.value.condition[0].source_address : []
  destination_address = each.value.condition[0].destination_address != null ? each.value.condition[0].destination_address : []
  /*application = each.value.condition != null ? each.value.condition.application : []
  url = each.value.condition != null ? each.value.condition.url  : []
  service = each.value.condition != null ? each.value.condition.service : []
  source_address = each.value.condition != null ? each.value.condition.source_address : []
  destination_address = each.value.condition != null ? each.value.condition.destination_address : []*/
  inspection = each.value.inspection
  after_rule = each.value.after_rule
  before_rule = each.value.before_rule
}

module secret {
  source  = "./modules/security/firewall/secret"
  for_each = var.secret != null || var.secret != {} ? var.secret : {}
  depends_on = [module.policy]
  secret_name = each.value.secret_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  secret_source = each.value.secret_source
  secret_type = each.value.secret_type
  vault_secret_id = each.value.vault_secret_id
  vault_name = each.value.vault_name
  compartment_id = each.value.vault_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.vault_compartment_id)) > 0 ? each.value.vault_compartment_id : var.compartment_ocids[each.value.vault_compartment_id]) : var.compartment_ocids[each.value.vault_compartment_id]
  version_number = each.value.version_number
}

module decryption_profile {
  source  = "./modules/security/firewall/decryption-profile"
  for_each = var.decryption_profile != null || var.decryption_profile != {} ? var.decryption_profile : {}
  depends_on = [module.policy, module.secret]
  profile_name = each.value.profile_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  profile_type = each.value.profile_type
  are_certificate_extensions_restricted = each.value.are_certificate_extensions_restricted
  is_auto_include_alt_name = each.value.is_auto_include_alt_name
  is_expired_certificate_blocked = each.value.is_expired_certificate_blocked
  is_out_of_capacity_blocked =each.value.is_out_of_capacity_blocked
  is_revocation_status_timeout_blocked = each.value.is_revocation_status_timeout_blocked
  is_unknown_revocation_status_blocked = each.value.is_unknown_revocation_status_blocked
  is_unsupported_cipher_blocked = each.value.is_unsupported_cipher_blocked
  is_unsupported_version_blocked = each.value.is_unsupported_version_blocked
  is_untrusted_issuer_blocked = each.value.is_untrusted_issuer_blocked
}

module decryption_rules {
  source                     = "./modules/security/firewall/decryption-rules"
  for_each                   = var.decryption_rules != null ? var.decryption_rules : {}
  depends_on = [module.policy, module.decryption_profile, module.secret, module.address_list]
  action = each.value.action
  rule_name = each.value.rule_name
  network_firewall_policy_id = length(regexall("ocid1.networkfirewallpolicy.oc1.*",each.value.network_firewall_policy_id)) > 0 ? each.value.network_firewall_policy_id : merge(module.policy.*...)[each.value.network_firewall_policy_id]["policy_tf_id"]
  source_address = each.value.condition[0].source_address != null  ? each.value.condition[0].source_address : []
  destination_address = each.value.condition[0].destination_address != null ? each.value.condition[0].destination_address : []
  after_rule = each.value.after_rule
  before_rule = each.value.before_rule
  decryption_profile = each.value.decryption_profile
  secret = each.value.secret
}

