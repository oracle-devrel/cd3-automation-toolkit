resource "oci_network_firewall_network_firewall_policy_application_group" "network_firewall_policy_application_group" {
    #Required
    apps = var.apps
    name = var.app_group_name
    network_firewall_policy_id = var.network_firewall_policy_id
}