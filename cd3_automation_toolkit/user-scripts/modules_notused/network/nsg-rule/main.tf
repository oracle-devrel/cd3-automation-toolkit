# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
    for_each = try((var.nsg_rules_details[var.key_name].options.icmp.0.code == null ? var.nsg_rules_details[var.key_name].options.icmp : []), try(var.nsg_rules_details[var.key_name].options.icmp.0.type != null ? var.nsg_rules_details[var.key_name].options.icmp : []), [])

    content {
      type = var.nsg_rules_details[var.key_name].options.icmp.0.type
    }
  }

  # ICMP Options
  # If type and code
  dynamic "icmp_options" {
    for_each = try((var.nsg_rules_details[var.key_name].options.icmp.0.code != null && var.nsg_rules_details[var.key_name].options.icmp.0.type != null ? var.nsg_rules_details[var.key_name].options.icmp : []), [])

    content {
      type = var.nsg_rules_details[var.key_name].options.icmp.0.type
      code = var.nsg_rules_details[var.key_name].options.icmp.0.code
    }
  }


  # TCP Options
  dynamic "tcp_options" {
    for_each = try(var.nsg_rules_details[var.key_name].options.tcp, [])

    content {
      #Optional
      dynamic "source_port_range" {
        for_each = try(var.nsg_rules_details[var.key_name].options.tcp.0.source_port_range_max != null || var.nsg_rules_details[var.key_name].options.tcp.0.source_port_range_min != null ? var.nsg_rules_details[var.key_name].options.tcp : [], [])

        content {
          #Required
          max = var.nsg_rules_details[var.key_name].options.tcp.0.source_port_range_max != null ? var.nsg_rules_details[var.key_name].options.tcp.0.source_port_range_max : null

          min = var.nsg_rules_details[var.key_name].options.tcp.0.source_port_range_min != null ? var.nsg_rules_details[var.key_name].options.tcp.0.source_port_range_min : null
        }
      }

      dynamic "destination_port_range" {
        for_each = try((var.nsg_rules_details[var.key_name].options.tcp.0.destination_port_range_max != null || var.nsg_rules_details[var.key_name].options.tcp.0.destination_port_range_min != null ? var.nsg_rules_details[var.key_name].options.tcp : []), [])

        content {
          #Required
          max = var.nsg_rules_details[var.key_name].options.tcp.0.destination_port_range_max != null ? var.nsg_rules_details[var.key_name].options.tcp.0.destination_port_range_max : null

          min = var.nsg_rules_details[var.key_name].options.tcp.0.destination_port_range_min != null ? var.nsg_rules_details[var.key_name].options.tcp.0.destination_port_range_min : null
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
        for_each = try((var.nsg_rules_details[var.key_name].options.udp.0.source_port_range_max != null || var.nsg_rules_details[var.key_name].options.udp.0.source_port_range_min != null ? var.nsg_rules_details[var.key_name].options.udp : []), [])

        content {
          #Required
          max = var.nsg_rules_details[var.key_name].options.udp.0.source_port_range_max != null ? var.nsg_rules_details[var.key_name].options.udp.0.source_port_range_max : null

          min = var.nsg_rules_details[var.key_name].options.udp.0.source_port_range_min != null ? var.nsg_rules_details[var.key_name].options.udp.0.source_port_range_min : null
        }
      }

      dynamic "destination_port_range" {
        for_each = try((var.nsg_rules_details[var.key_name].options.udp.0.destination_port_range_max != null || var.nsg_rules_details[var.key_name].options.udp.0.destination_port_range_min != null ? var.nsg_rules_details[var.key_name].options.udp : []), [])

        content {
          #Required
          max = var.nsg_rules_details[var.key_name].options.udp.0.destination_port_range_max != null ? var.nsg_rules_details[var.key_name].options.udp.0.destination_port_range_max : null

          min = var.nsg_rules_details[var.key_name].options.udp.0.destination_port_range_min != null ? var.nsg_rules_details[var.key_name].options.udp.0.destination_port_range_min : null
        }
      }
    }
  }
}
