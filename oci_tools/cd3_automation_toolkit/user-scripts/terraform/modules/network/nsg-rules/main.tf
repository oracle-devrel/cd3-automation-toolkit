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
    for_each = try((var.nsg_rules_details[var.key_name].options.icmp[0].code == "" && var.nsg_rules_details[var.key_name].options.icmp[0].type != "" ? var.nsg_rules_details[var.key_name].options.icmp : []), [])

    content {
      type = icmp_options.value.type
    }
  }

  # ICMP Options
  # If type and code
  dynamic "icmp_options" {
    for_each = try((var.nsg_rules_details[var.key_name].options.icmp[0].code != "" && var.nsg_rules_details[var.key_name].options.icmp[0].type != "" ? var.nsg_rules_details[var.key_name].options.icmp : []), [])

    content {
      type = icmp_options.value.type
      code = icmp_options.value.code
    }
  }


  # TCP Options
  dynamic "tcp_options" {
    for_each = try((var.nsg_rules_details[var.key_name].options.tcp != [] ? var.nsg_rules_details[var.key_name].options.tcp : []), [])

    content {
      #Optional
      dynamic "source_port_range" {
        for_each = try((tcp_options.value.source_port_range_max != "" || tcp_options.value.source_port_range_min != "" ? tcp_options.value : []), [])

        content {
          #Required
          max = source_port_range.value.source_port_range_max != "" ? source_port_range.value.source_port_range_max : ""

          min = source_port_range.value.source_port_range_min != "" ? source_port_range.value.source_port_range_min : ""
        }
      }

      dynamic "destination_port_range" {
        for_each = try((tcp_options.value.destination_port_range_max != "" || tcp_options.value.destination_port_range_min != "" ? tcp_options.value : []), [])

        content {
          #Required
          max = destination_port_range.value.destination_port_range_max != "" ? destination_port_range.value.destination_port_range_max : ""

          min = destination_port_range.value.destination_port_range_min != "" ? destination_port_range.value.destination_port_range_min : ""
        }
      }
    }
  }

  # UDP Options
  dynamic "udp_options" {
    for_each = try((var.nsg_rules_details[var.key_name].options.udp != [] ? var.nsg_rules_details[var.key_name].options.udp : []), [])

    content {
      #Optional
      dynamic "source_port_range" {
        for_each = try((udp_options.value.source_port_range_max != "" || udp_options.value.source_port_range_min != "" ? udp_options.value : []), [])

        content {
          #Required
          max = source_port_range.value.source_port_range_max != "" ? source_port_range.value.source_port_range_max : ""

          min = source_port_range.value.source_port_range_min != "" ? source_port_range.value.source_port_range_min : ""
        }
      }

      dynamic "destination_port_range" {
        for_each = try((udp_options.value.destination_port_range_max != "" || udp_options.value.destination_port_range_min != "" ? udp_options.value : []), [])

        content {
          #Required
          max = destination_port_range.value.destination_port_range_max != "" ? destination_port_range.value.destination_port_range_max : ""

          min = destination_port_range.value.destination_port_range_min != "" ? destination_port_range.value.destination_port_range_min : ""
        }
      }
    }
  }
}