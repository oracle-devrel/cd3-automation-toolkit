// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Security List
############################

resource "oci_core_security_list" "security_list" {

  #Required
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags

  dynamic "ingress_security_rules" {
    for_each = var.seclist_details[var.key_name].ingress_sec_rules != [] ? var.seclist_details[var.key_name].ingress_sec_rules : []

    content {
      #Required
      protocol = ingress_security_rules.value.protocol
      source   = ingress_security_rules.value.source

      #Optional
      description = ingress_security_rules.value.description

      # If type and code
      dynamic "icmp_options" {
        for_each = ingress_security_rules.value.icmp_options[0].icmp_options_code != "" && ingress_security_rules.value.icmp_options[0].icmp_options_type != "" ? ingress_security_rules.value.icmp_options : []
        content {
          #Required
          type = ingress_security_rules.value.icmp_options[0].icmp_options_type

          #Optional
          code = ingress_security_rules.value.icmp_options[0].icmp_options_code != null || ingress_security_rules.value.icmp_options[0].icmp_options_code != "" ? ingress_security_rules.value.icmp_options[0].icmp_options_code : null
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = ingress_security_rules.value.icmp_options[0].icmp_options_code == "" && ingress_security_rules.value.icmp_options[0].icmp_options_type != "" ? ingress_security_rules.value.icmp_options : []
        content {
          #Required
          type = ingress_security_rules.value.icmp_options[0].icmp_options_type
        }
      }

      source_type = ingress_security_rules.value.source_type != null ? ingress_security_rules.value.source_type : null
      stateless   = ingress_security_rules.value.stateless

      dynamic "tcp_options" {
        for_each = ingress_security_rules.value.tcp_options != [] ? ingress_security_rules.value.tcp_options : []
        content {
          min = tcp_options.value.tcp_options_destination_port_range_min != null ? tcp_options.value.tcp_options_destination_port_range_min : null
          max = tcp_options.value.tcp_options_destination_port_range_max != null ? tcp_options.value.tcp_options_destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = tcp_options.value.tcp_source_ports != [] ? tcp_options.value.tcp_source_ports : []
            content {
              #Required
              max = source_port_range.value.tcp_options_source_port_range_max != null ? source_port_range.value.tcp_options_source_port_range_max : null
              min = source_port_range.value.tcp_options_source_port_range_min != null ? source_port_range.value.tcp_options_source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = ingress_security_rules.value.udp_options != [] ? ingress_security_rules.value.udp_options : []
        content {
          #Optional
          max = udp_options.value.udp_options_destination_port_range_max != null ? udp_options.value.udp_options_destination_port_range_max : null
          min = udp_options.value.udp_options_destination_port_range_min != null ? udp_options.value.udp_options_destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = udp_options.value.udp_source_ports != [] ? udp_options.value.udp_source_ports : []
            content {
              #Required
              max = source_port_range.value.udp_options_source_port_range_max != null ? source_port_range.value.udp_options_source_port_range_max : null
              min = source_port_range.value.udp_options_source_port_range_min != null ? source_port_range.value.udp_options_source_port_range_min : null
            }
          }
        }
      }
    }
  }

  dynamic "egress_security_rules" {
    for_each = var.seclist_details[var.key_name].egress_sec_rules != [] ? var.seclist_details[var.key_name].egress_sec_rules : []

    content {
      #Required
      protocol    = egress_security_rules.value.protocol
      destination = egress_security_rules.value.destination

      #Optional
      description = egress_security_rules.value.description

      #If type and code
      dynamic "icmp_options" {
        for_each = egress_security_rules.value.icmp_options[0].icmp_options_type != "" && egress_security_rules.value.icmp_options[0].icmp_options_code != "" ? egress_security_rules.value.icmp_options : []
        content {
          #Required
          type = egress_security_rules.value.icmp_options[0].icmp_options_type

          #Optional
          code = egress_security_rules.value.icmp_options[0].icmp_options_code != null || egress_security_rules.value.icmp_options[0].icmp_options_code != "" ? egress_security_rules.value.icmp_options[0].icmp_options_code : null
        }
      }

      #If type and no code
      dynamic "icmp_options" {
        for_each = egress_security_rules.value.icmp_options[0].icmp_options_type != "" && egress_security_rules.value.icmp_options[0].icmp_options_code == "" ? egress_security_rules.value.icmp_options : []
        content {
          #Required
          type = egress_security_rules.value.icmp_options[0].icmp_options_type

        }
      }

      destination_type = egress_security_rules.value.destination_type != null ? egress_security_rules.value.destination_type : null
      stateless        = egress_security_rules.value.stateless

      dynamic "tcp_options" {
        for_each = egress_security_rules.value.tcp_options != [] ? egress_security_rules.value.tcp_options : []
        content {
          min = tcp_options.value.tcp_options_destination_port_range_min != null ? tcp_options.value.tcp_options_destination_port_range_min : null
          max = tcp_options.value.tcp_options_destination_port_range_max != null ? tcp_options.value.tcp_options_destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = tcp_options.value.tcp_source_ports != [] ? tcp_options.value.tcp_source_ports : []
            content {
              #Required
              max = source_port_range.value.tcp_options_source_port_range_max != null ? source_port_range.value.tcp_options_source_port_range_max: null
              min = source_port_range.value.tcp_options_source_port_range_min != null ? source_port_range.value.tcp_options_source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = egress_security_rules.value.udp_options != [] ? egress_security_rules.value.udp_options : []
        content {
          #Optional
          max = udp_options.value.udp_options_destination_port_range_max != null ? udp_options.value.udp_options_destination_port_range_max : null
          min = udp_options.value.udp_options_destination_port_range_min != null ? udp_options.value.udp_options_destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = udp_options.value.udp_source_ports != [] ? udp_options.value.udp_source_ports : []
            content {
              #Required
              max = source_port_range.value.udp_options_source_port_range_max != null ? source_port_range.value.udp_options_source_port_range_max : null
              min = source_port_range.value.udp_options_source_port_range_min != null ? source_port_range.value.udp_options_source_port_range_min : null
            }
          }
        }
      }
    }
  }
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}