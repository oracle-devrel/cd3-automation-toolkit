resource "oci_network_firewall_network_firewall_policy_url_list" "network_firewall_policy_url_list" {
  name = var.urllist_name
  network_firewall_policy_id = var.network_firewall_policy_id
  dynamic "urls" {
    for_each = var.urls_details != null ? var.urls_details : []
    content {
      pattern = urls.value.pattern
      type    = urls.value.type
    }
  }
}
