resource "oci_network_firewall_network_firewall_policy_decryption_rule" "network_firewall_policy_decryption_rule" {
  lifecycle {
        ignore_changes = [position]
    }
  name = var.rule_name
  action = var.action
  network_firewall_policy_id = var.network_firewall_policy_id
  condition {
      destination_address = var.destination_address
      source_address = var.source_address
      }
  decryption_profile = var.decryption_profile
  secret  = var.secret
  position {
      after_rule = var.after_rule
      before_rule = var.before_rule
  }
}
