// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Network Security Groups
############################

resource "oci_core_network_security_group" "network_security_group" {

    count = (var.display_name != null  && var.display_name != "") ? 1 : 0
    #Required
    compartment_id = var.compartment_id
    vcn_id = var.vcn_id

    #Optional
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags

    lifecycle {
        ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"]]
        }
}