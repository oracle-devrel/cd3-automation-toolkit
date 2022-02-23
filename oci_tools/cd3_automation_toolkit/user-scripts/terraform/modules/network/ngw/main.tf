// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create NAT Gateway
############################

resource "oci_core_nat_gateway" "nat_gateway" {
    #Required
    count = (var.display_name != null  && var.display_name != "") ? 1 : 0
    compartment_id = var.compartment_id
    vcn_id = var.vcn_id

    #Optional
    public_ip_id = var.public_ip_id
    block_traffic = var.block_traffic
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags

    lifecycle {
      ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
  }
}