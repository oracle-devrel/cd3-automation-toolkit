// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Default Security List
############################

resource "oci_core_default_security_list" "default_security_list" {

  #Required
  manage_default_resource_id = var.manage_default_resource_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags

  dynamic "ingress_security_rules" {
    for_each = try((var.seclist_details[var.key_name].ingress_sec_rules != [] && var.seclist_details[var.key_name].ingress_sec_rules.0.protocol != null ? var.seclist_details[var.key_name].ingress_sec_rules : []), [])

    content {
      #Required
      protocol = ingress_security_rules.value.protocol
      source   = ingress_security_rules.value.source

      #Optional
      description = ingress_security_rules.value.description

      # If type and code
      dynamic "icmp_options" {
        for_each = try((ingress_security_rules.value.options.icmp.code != "" && ingress_security_rules.value.options.icmp.type != "" ? ingress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = icmp_options.value.type

          #Optional
          code = icmp_options.value.code != null || icmp_options.value.code != "" ? icmp_options.value.code : null
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = try((ingress_security_rules.value.options.icmp.code == "" && ingress_security_rules.value.options.icmp.type != "" ? ingress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = icmp_options.value.type
        }
      }

      source_type = try(ingress_security_rules.value.source_type, null)
      stateless   = try(ingress_security_rules.value.stateless, null)

      dynamic "tcp_options" {
        for_each = try((ingress_security_rules.value.options.tcp != [] ? ingress_security_rules.value.options.tcp : []), [])
        content {
          min = tcp_options.value.tcp_destination_port_range_min != null ? tcp_options.value.tcp_destination_port_range_min : null
          max = tcp_options.value.tcp_destination_port_range_max != null ? tcp_options.value.tcp_destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = try((tcp_options.value.tcp_source_port_range_min != "" || tcp_options.value.tcp_source_port_range_max != "" ? tcp_options.value : []), [])
            content {
              #Required
              max = source_port_range.value.tcp_source_port_range_max != null ? source_port_range.value.tcp_source_port_range_max : null
              min = source_port_range.value.tcp_source_port_range_min != null ? source_port_range.value.tcp_source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = try((ingress_security_rules.value.options.udp != [] && var.seclist_details[var.key_name].ingress_sec_rules.0.protocol != null ? ingress_security_rules.value.options.udp : []), [])
        content {
          #Optional
          max = udp_options.value.udp_destination_port_range_max != null ? udp_options.value.udp_destination_port_range_max : null
          min = udp_options.value.udp_destination_port_range_min != null ? udp_options.value.udp_destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = try((udp_options.value.tcp_source_port_range_min != "" || udp_options.value.tcp_source_port_range_max != "" != [] ? udp_options.value : []), [])
            content {
              #Required
              max = source_port_range.value.udp_source_port_range_max != null ? source_port_range.value.udp_source_port_range_max : null
              min = source_port_range.value.udp_source_port_range_min != null ? source_port_range.value.udp_source_port_range_min : null
            }
          }
        }
      }
    }
  }

  dynamic "egress_security_rules" {
    for_each = try((var.seclist_details[var.key_name].egress_sec_rules != [] && var.seclist_details[var.key_name].egress_sec_rules.0.protocol != null ? var.seclist_details[var.key_name].egress_sec_rules : []), [])

    content {
      #Required
      protocol    = egress_security_rules.value.protocol
      destination = egress_security_rules.value.destination

      #Optional
      description = egress_security_rules.value.description

      # If type and code
      dynamic "icmp_options" {
        for_each = try((egress_security_rules.value.options.icmp[0].code != "" && egress_security_rules.value.options.icmp[0].type != "" ? egress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = icmp_options.value.type

          #Optional
          code = icmp_options.value.code != null || icmp_options.value.code != "" ? icmp_options.value.code : null
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = try((egress_security_rules.value.options.icmp[0].code == "" && egress_security_rules.value.options.icmp[0].type != "" ? egress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = icmp_options.value.type
        }
      }

      destination_type = try(egress_security_rules.value.destination_type, null)
      stateless        = try(egress_security_rules.value.stateless, null)

      dynamic "tcp_options" {
        for_each = try((egress_security_rules.value.options.tcp != [] ? egress_security_rules.value.options.tcp : []), [])
        content {
          min = tcp_options.value.tcp_destination_port_range_min != null ? tcp_options.value.tcp_destination_port_range_min : null
          max = tcp_options.value.tcp_destination_port_range_max != null ? tcp_options.value.tcp_destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = try((tcp_options.value.tcp_source_port_range_min != "" || tcp_options.value.tcp_source_port_range_max != "" ? tcp_options.value : []), [])
            content {
              #Required
              max = source_port_range.value.tcp_source_port_range_max != null ? source_port_range.value.tcp_source_port_range_max : null
              min = source_port_range.value.tcp_source_port_range_min != null ? source_port_range.value.tcp_source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = try((egress_security_rules.value.options.udp != [] ? egress_security_rules.value.options.udp : []), [])
        content {
          #Optional
          max = udp_options.value.udp_destination_port_range_max != null ? udp_options.value.udp_destination_port_range_max : null
          min = udp_options.value.udp_destination_port_range_min != null ? udp_options.value.udp_destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = try((udp_options.value.tcp_source_port_range_min != "" || udp_options.value.tcp_source_port_range_max != "" != [] ? udp_options.value : []), [])
            content {
              #Required
              max = source_port_range.value.udp_source_port_range_max != null ? source_port_range.value.udp_source_port_range_max : null
              min = source_port_range.value.udp_source_port_range_min != null ? source_port_range.value.udp_source_port_range_min : null
            }
          }
        }
      }
    }
  }
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}