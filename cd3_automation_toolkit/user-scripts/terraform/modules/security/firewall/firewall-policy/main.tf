resource "oci_network_firewall_network_firewall_policy" "network_firewall_policy" {
  compartment_id = var.compartment_id
  display_name = var.display_name
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"],defined_tags["SE_Details.SE_Name"]]
  }

}

