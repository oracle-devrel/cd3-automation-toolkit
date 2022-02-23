// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create VCNs
############################

data "oci_identity_availability_domains" "demo_availability_domains" {
  #Required
  compartment_id = var.compartment_id
}

resource "oci_core_vcn" "vcn" {
    count          = (var.display_name != null  && var.display_name != "")  ? 1 : 0

    #Required
    compartment_id = var.compartment_id

    #Optional
    cidr_blocks = var.cidr_blocks
    defined_tags = var.defined_tags
    display_name = var.display_name
    dns_label = var.dns_label
    freeform_tags = var.freeform_tags
    is_ipv6enabled = var.is_ipv6enabled

    lifecycle {
      create_before_destroy = true
      ignore_changes = [cidr_blocks,defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],cidr_blocks]
  }
}