# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create Default DHCP Options
############################

resource "oci_core_default_dhcp_options" "default_dhcp_option" {

  # Required
  manage_default_resource_id = var.manage_default_resource_id

  options {
    type               = "DomainNameServer"
    server_type        = var.server_type
    custom_dns_servers = var.custom_dns_servers
  }

  dynamic "options" {
    for_each = try(var.search_domain_names, [])
    content {
      type                = "SearchDomain"
      search_domain_names = var.search_domain_names
    }
  }

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}