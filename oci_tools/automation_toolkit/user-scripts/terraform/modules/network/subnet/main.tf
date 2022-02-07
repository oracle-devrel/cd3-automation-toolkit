// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Subnets
############################

data "oci_identity_availability_domains" "availability_domains" {
  #Required
  compartment_id = var.tenancy_ocid
}

resource "oci_core_subnet" "subnet" {

    count = (var.display_name != null  && var.display_name != "") ? 1 : 0
    #Required
    cidr_block = var.cidr_block
    compartment_id = var.compartment_id
    vcn_id = var.vcn_id

    #Optional
    availability_domain = (var.availability_domain != "" && var.availability_domain != null) ? ({ for k,v in data.oci_identity_availability_domains.availability_domains.availability_domains : v.name => v.id } [var.availability_domain]) : ""
    defined_tags = var.defined_tags
    dhcp_options_id = var.dhcp_options_id
    display_name = var.display_name
    dns_label = var.dns_label
    freeform_tags = var.freeform_tags
    ipv6cidr_block = var.ipv6cidr_block
    prohibit_internet_ingress = var.prohibit_internet_ingress
    prohibit_public_ip_on_vnic = var.prohibit_public_ip_on_vnic
    route_table_id = var.route_table_id
    security_list_ids = var.security_list_ids
    
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"]]
    }
}