// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Custom DHCP Options
############################

resource "oci_core_dhcp_options" "custom_dhcp_option" {

  #Required
  compartment_id = var.compartment_id
  options {
    type               = "DomainNameServer"
    server_type        = var.server_type
    custom_dns_servers = var.custom_dns_servers
  }

  dynamic "options" {
    for_each = var.search_domain_names
    content {
      type                = "SearchDomain"
      search_domain_names = options.value
    }
  }

  vcn_id = var.vcn_id

  #Optional
  defined_tags     = var.defined_tags
  display_name     = var.display_name
  domain_name_type = var.domain_name_type
  freeform_tags    = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}