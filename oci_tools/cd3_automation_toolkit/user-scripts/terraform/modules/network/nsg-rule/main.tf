// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Network Security Group Rules
############################


resource "oci_core_network_security_group_security_rule" "nsg_rule" {

  #Required
  network_security_group_id = var.nsg_id
  direction                 = var.direction
  protocol                  = var.protocol

  #Optional
  description      = var.description
  destination      = var.destination_addr
  destination_type = var.destination_type
  source           = var.source_addr
  source_type      = var.source_type
  stateless        = var.stateless

  # ICMP Options
  # If type and no code
  dynamic "icmp_options" {
    for_each = var.nsg_rules_details[var.key_name].icmp_options[0].icmp_code == "" && var.nsg_rules_details[var.key_name].icmp_options[0].icmp_type != "" ? var.nsg_rules_details[var.key_name].icmp_options : []

    content {
      type = icmp_options.value.icmp_type
    }
  }

  # ICMP Options
  # If type and code
  dynamic "icmp_options" {
    for_each = var.nsg_rules_details[var.key_name].icmp_options[0].icmp_code != "" && var.nsg_rules_details[var.key_name].icmp_options[0].icmp_type != "" ? var.nsg_rules_details[var.key_name].icmp_options : []

    content {
      type = icmp_options.value.icmp_type
      code = icmp_options.value.icmp_code
    }
  }


  # TCP Options
  dynamic "tcp_options" {
    for_each = var.nsg_rules_details[var.key_name].tcp_options != [] ? var.nsg_rules_details[var.key_name].tcp_options : []

    content {
      #Optional
      dynamic "source_port_range" {
        for_each = tcp_options.value["source_port_range"] != [] ? tcp_options.value["source_port_range"] : []

        content {
          #Required
          max = tcp_options.value["source_port_range"][0].tcp_options_source_port_max != "" ? tcp_options.value["source_port_range"][0].tcp_options_source_port_max : ""

          min = tcp_options.value["source_port_range"][0].tcp_options_source_port_min != "" ? tcp_options.value["source_port_range"][0].tcp_options_source_port_min : ""
        }
      }

      dynamic "destination_port_range" {
        for_each = tcp_options.value["destination_port_range"] != [] ? tcp_options.value["destination_port_range"] : []

        content {
          #Required
          max = tcp_options.value["destination_port_range"][0].tcp_options_destination_port_max != "" ? tcp_options.value["destination_port_range"][0].tcp_options_destination_port_max : ""

          min = tcp_options.value["destination_port_range"][0].tcp_options_destination_port_min != "" ? tcp_options.value["destination_port_range"][0].tcp_options_destination_port_min : ""
        }
      }
    }
  }

  # UDP Options
  dynamic "udp_options" {
    for_each = var.nsg_rules_details[var.key_name].udp_options != [] ? var.nsg_rules_details[var.key_name].udp_options : []

    content {
      #Optional
      dynamic "source_port_range" {
        for_each = udp_options.value["source_port_range"] != [] ? udp_options.value["source_port_range"] : []

        content {
          #Required
          max = udp_options.value["source_port_range"][0].udp_options_source_port_max != "" ? udp_options.value["source_port_range"][0].udp_options_source_port_max : ""

          min = udp_options.value["source_port_range"][0].udp_options_source_port_min != "" ? udp_options.value["source_port_range"][0].udp_options_source_port_min : ""
        }

      }


      #Optional
      dynamic "destination_port_range" {
        for_each = udp_options.value["destination_port_range"] != [] ? udp_options.value["destination_port_range"] : []

        content {
          #Required
          max = udp_options.value["destination_port_range"][0].udp_options_destination_port_max != "" ? udp_options.value["destination_port_range"][0].udp_options_destination_port_max : ""


          min = udp_options.value["destination_port_range"][0].udp_options_destination_port_min != "" ? udp_options.value["destination_port_range"][0].udp_options_destination_port_min : ""
        }
      }
    }
  }
}
