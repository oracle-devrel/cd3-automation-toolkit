// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Networking
# Create Default DHCP Options
############################

resource "oci_core_default_dhcp_options" "default_dhcp_option" {
    count = (var.server_type != null  && var.server_type != "") ? 1 : 0
    manage_default_resource_id  = var.manage_default_resource_id

    options {
            type = "DomainNameServer"
            server_type = var.server_type
            }

    options {
            type = "SearchDomain"
            search_domain_names = var.search_domain_names
            }

    #Optional
    defined_tags = var.defined_tags
    freeform_tags = var.freeform_tags

    lifecycle {
        ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
        }
 }