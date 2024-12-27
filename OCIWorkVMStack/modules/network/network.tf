


resource "oci_core_vcn" "vcn" {
  count          = local.create_vcn
  compartment_id = var.vcn_compartment_ocid
  /*
#Optional
  dynamic "byoipv6cidr_details" {
    for_each = try(var.byoipv6cidr_details != [] ? var.byoipv6cidr_details : [], [])
    content {
      #Required
      byoipv6range_id = byoipv6cidr_details.value.byoipv6range_id
      ipv6cidr_block  = byoipv6cidr_details.value.ipv6cidr_block
    }
  }
*/
  cidr_block = var.vcn_cidr
  # defined_tags                     = var.defined_tags
  display_name = var.vcn_name
  dns_label    = var.vcn_dns_label
  # freeform_tags                    = var.freeform_tags
  # is_ipv6enabled                   = var.is_ipv6enabled
  # ipv6private_cidr_blocks          = var.ipv6private_cidr_blocks
  # is_oracle_gua_allocation_enabled = var.is_oracle_gua_allocation_enabled
  lifecycle {
    create_before_destroy = true
  }

}

resource "oci_core_internet_gateway" "internet_gw" {
  count          = local.create_inet_gw
  compartment_id = var.vcn_compartment_ocid
  display_name   = "${var.vcn_name}-igw"
  vcn_id         = local.vcn_id
}

resource "oci_core_nat_gateway" "nat_gw" {
  count          = local.create_nat_gw
  compartment_id = var.vcn_compartment_ocid
  display_name   = "${var.vcn_name}-ngw"
  vcn_id         = local.vcn_id
}

resource "oci_core_route_table" "rt" {
  count          = local.create_vcn
  compartment_id = var.vcn_compartment_ocid
  vcn_id         = local.vcn_id
  display_name   = "${var.subnet_name}-rt"

 # Route rules to NGW or IGW
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = local.create_inet_gw == 1 ? oci_core_internet_gateway.internet_gw[0].id : oci_core_nat_gateway.nat_gw[0].id
  }

 # Route rules to DRG
 dynamic route_rules {
  for_each = local.route_rule_drg
  content {
     destination       = route_rules.value
     destination_type  = "CIDR_BLOCK"
     network_entity_id = var.existing_drg_id
   }
 }

}
resource "oci_core_security_list" "security_list" {
  count          = local.create_vcn
  compartment_id = var.vcn_compartment_ocid
  vcn_id         = local.vcn_id
  display_name   = "${var.subnet_name}-sl"
  ingress_security_rules {
    protocol    = "all"
    source      = var.subnet_cidr
    source_type = "CIDR_BLOCK"
  }
  egress_security_rules {
    # All traffic for all ports
    protocol         = "all"
    destination_type = "CIDR_BLOCK"
    destination      = "0.0.0.0/0"
  }
}

resource "oci_core_subnet" "subnet" {
  count          = local.create_vcn
  compartment_id = var.vcn_compartment_ocid
  vcn_id         = local.vcn_id
  display_name   = var.subnet_name
  cidr_block     = var.subnet_cidr
  dns_label      = var.subnet_dns_label

  # Controls creation of Private vs Public subnet
  prohibit_public_ip_on_vnic = var.subnet_type == "Public" ? false : true
  route_table_id             = oci_core_route_table.rt[0].id
  security_list_ids          = [oci_core_security_list.security_list[0].id]
  # Prevent lifecycle changes until we have tested that can be updated
  lifecycle {
    ignore_changes = []
  }
}

resource "oci_core_network_security_group" "nsg" {
  count          = local.create_vcn
  compartment_id = var.vcn_compartment_ocid
  vcn_id         = local.vcn_id
  display_name   = "${var.subnet_name}-nsg"
}

resource "oci_core_network_security_group_security_rule" "nsg_rule_1" {
  count = local.create_nsg_rule == 1 ? length(var.source_cidr) : 0
  #Required
  network_security_group_id = oci_core_network_security_group.nsg[0].id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = var.source_cidr[count.index]
  source_type               = "CIDR_BLOCK"
  stateless                 = false
  tcp_options {
    destination_port_range {
      #Required
      max = "22"
      min = "22"
    }
  }

}

resource "oci_core_network_security_group_security_rule" "nsg_rule_2" {
  count = local.create_nsg_rule == 1 ? length(var.source_cidr) : 0
  #Required
  network_security_group_id = oci_core_network_security_group.nsg[0].id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = var.source_cidr[count.index]
  source_type               = "CIDR_BLOCK"
  stateless                 = false
  tcp_options {
    destination_port_range {
      #Required
      max = "8443"
      min = "8443"
    }
  }

}


resource "oci_core_drg_attachment" "drg_attachment" {

  count = var.drg_attachment == true ? 1 : 0
  #Required
  drg_id       = var.existing_drg_id
  display_name = "${var.vcn_name}-attachment"
  #drg_route_table_id = oci_core_drg_route_table.test_drg_route_table.id

  network_details {
    #Required
    id   = local.vcn_id
    type = "VCN"

    #Optional
    #route_table_id = oci_core_route_table.test_route_table.id
    #vcn_route_type = var.drg_attachment_network_details_vcn_route_type
  }
}