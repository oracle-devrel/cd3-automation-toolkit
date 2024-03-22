resource "oci_network_firewall_network_firewall_policy_address_list" "network_firewall_policy_address_list" {
  name = var.address_list_name
  network_firewall_policy_id = var.network_firewall_policy_id
  type = var.address_type
  addresses = var.addresses
}
