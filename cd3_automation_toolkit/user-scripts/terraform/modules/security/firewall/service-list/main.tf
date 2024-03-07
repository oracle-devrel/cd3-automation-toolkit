resource "oci_network_firewall_network_firewall_policy_service_list"  "network_firewall_policy_service_list" {
  name                       = var.service_list_name
  network_firewall_policy_id = var.network_firewall_policy_id
  services                   = var.services
  #services                   = var.services != null ? (local.services == null ? ["INVALID SERVICE"] : local.services) : null
}