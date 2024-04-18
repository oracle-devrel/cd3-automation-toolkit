// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Subnets
############################

resource "oci_core_subnet" "subnet" {

  #Required
  cidr_block     = var.cidr_block
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

  #Optional
  availability_domain        = var.availability_domain
  defined_tags               = var.defined_tags
  dhcp_options_id            = var.dhcp_options_id
  display_name               = var.display_name
  dns_label                  = var.dns_label
  freeform_tags              = var.freeform_tags
  ipv6cidr_block             = var.ipv6cidr_block
  prohibit_internet_ingress  = var.prohibit_internet_ingress
  prohibit_public_ip_on_vnic = var.prohibit_public_ip_on_vnic
  route_table_id             = var.route_table_id
  security_list_ids          = flatten([for seclist in var.security_list_ids : [for sl in seclist : sl if length(regexall("ocid1.securitylist.oc1*", sl)) > 0 ]])
}
