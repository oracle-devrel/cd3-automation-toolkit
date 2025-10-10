# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create Security List
############################

resource "oci_core_security_list" "security_list" {

count = var.default_seclist ==true ? 0 : 1
  #Required
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

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
        for_each = try((ingress_security_rules.value.options.icmp.0.code != null && ingress_security_rules.value.options.icmp.0.type != null ? ingress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = ingress_security_rules.value.options.icmp.0.type
          #Optional
          code = ingress_security_rules.value.options.icmp.0.code
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = try((ingress_security_rules.value.options.icmp.0.code == null ? ingress_security_rules.value.options.icmp : []), try(ingress_security_rules.value.options.icmp.0.type != null ? ingress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = ingress_security_rules.value.options.icmp.0.type
        }
      }

      source_type = try(ingress_security_rules.value.source_type, null)
      stateless   = try(ingress_security_rules.value.stateless, null)

      dynamic "tcp_options" {
        for_each = try((ingress_security_rules.value.options.tcp != [] ? ingress_security_rules.value.options.tcp : []), [])
        content {
          min = tcp_options.value.destination_port_range_min != null ? tcp_options.value.destination_port_range_min : null
          max = tcp_options.value.destination_port_range_max != null ? tcp_options.value.destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = try((tcp_options.value.source_port_range_min != null || tcp_options.value.source_port_range_max != null ? ingress_security_rules.value.options.tcp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = try((ingress_security_rules.value.options.udp != [] ? ingress_security_rules.value.options.udp : []), [])
        content {
          #Optional
          max = udp_options.value.destination_port_range_max != null ? udp_options.value.destination_port_range_max : null
          min = udp_options.value.destination_port_range_min != null ? udp_options.value.destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = try((udp_options.value.source_port_range_min != null || udp_options.value.source_port_range_max != null != [] ? ingress_security_rules.value.options.udp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
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
        for_each = try((egress_security_rules.value.options.icmp.0.code != null && egress_security_rules.value.options.icmp.0.type != null ? egress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = egress_security_rules.value.options.icmp.0.type
          #Optional
          code = egress_security_rules.value.options.icmp.0.code
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = try((egress_security_rules.value.options.icmp.0.code == null ? egress_security_rules.value.options.icmp : []), try(egress_security_rules.value.options.icmp.0.type != null ? egress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = egress_security_rules.value.options.icmp.0.type
        }
      }


      destination_type = try(egress_security_rules.value.destination_type, null)
      stateless        = try(egress_security_rules.value.stateless, null)

      dynamic "tcp_options" {
        for_each = try((egress_security_rules.value.options.tcp != [] ? egress_security_rules.value.options.tcp : []), [])
        content {
          min = tcp_options.value.destination_port_range_min != null ? tcp_options.value.destination_port_range_min : null
          max = tcp_options.value.destination_port_range_max != null ? tcp_options.value.destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = try((tcp_options.value.source_port_range_min != null || tcp_options.value.source_port_range_max != null ? egress_security_rules.value.options.tcp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = try((egress_security_rules.value.options.udp != [] ? egress_security_rules.value.options.udp : []), [])
        content {
          #Optional
          max = udp_options.value.destination_port_range_max != null ? udp_options.value.destination_port_range_max : null
          min = udp_options.value.destination_port_range_min != null ? udp_options.value.destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = try((udp_options.value.source_port_range_min != null || udp_options.value.source_port_range_max != null != [] ? egress_security_rules.value.options.udp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
            }
          }
        }
      }
    }
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "oci_core_default_security_list" "default_security_list" {
count = var.default_seclist ==true ? 1 : 0


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
        for_each = try((ingress_security_rules.value.options.icmp.0.code != null && ingress_security_rules.value.options.icmp.0.type != null ? ingress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = ingress_security_rules.value.options.icmp.0.type

          #Optional
          code = ingress_security_rules.value.options.icmp.0.code
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = try((ingress_security_rules.value.options.icmp.0.code == null ? ingress_security_rules.value.options.icmp : []), try(ingress_security_rules.value.options.icmp.0.type != null ? ingress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = ingress_security_rules.value.options.icmp.0.type
        }
      }

      source_type = try(ingress_security_rules.value.source_type, null)
      stateless   = try(ingress_security_rules.value.stateless, null)

      dynamic "tcp_options" {
        for_each = try((ingress_security_rules.value.options.tcp != [] ? ingress_security_rules.value.options.tcp : []), [])
        content {
          min = tcp_options.value.destination_port_range_min != null ? tcp_options.value.destination_port_range_min : null
          max = tcp_options.value.destination_port_range_max != null ? tcp_options.value.destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = try((tcp_options.value.source_port_range_min != null || tcp_options.value.source_port_range_max != null ? ingress_security_rules.value.options.tcp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = try((ingress_security_rules.value.options.udp != [] && var.seclist_details[var.key_name].ingress_sec_rules.0.protocol != null ? ingress_security_rules.value.options.udp : []), [])
        content {
          #Optional
          max = udp_options.value.destination_port_range_max != null ? udp_options.value.destination_port_range_max : null
          min = udp_options.value.destination_port_range_min != null ? udp_options.value.destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = try((udp_options.value.source_port_range_min != null || udp_options.value.source_port_range_max != null != [] ? ingress_security_rules.value.options.udp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
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
        for_each = try((egress_security_rules.value.options.icmp.0.code != null && egress_security_rules.value.options.icmp.0.type != null ? egress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = egress_security_rules.value.options.icmp.0.type
          #Optional
          code = egress_security_rules.value.options.icmp.0.code
        }
      }

      # If type and no code
      dynamic "icmp_options" {
        for_each = try((egress_security_rules.value.options.icmp.0.code == null ? egress_security_rules.value.options.icmp : []), try(egress_security_rules.value.options.icmp.0.type != null ? egress_security_rules.value.options.icmp : []), [])
        content {
          #Required
          type = egress_security_rules.value.options.icmp.0.type
        }
      }


      destination_type = try(egress_security_rules.value.destination_type, null)
      stateless        = try(egress_security_rules.value.stateless, null)

      dynamic "tcp_options" {
        for_each = try((egress_security_rules.value.options.tcp != [] ? egress_security_rules.value.options.tcp : []), [])
        content {
          min = tcp_options.value.destination_port_range_min != null ? tcp_options.value.destination_port_range_min : null
          max = tcp_options.value.destination_port_range_max != null ? tcp_options.value.destination_port_range_max : null
          dynamic "source_port_range" {
            for_each = try((tcp_options.value.source_port_range_min != null || tcp_options.value.source_port_range_max != null ? egress_security_rules.value.options.tcp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
            }
          }
        }
      }

      dynamic "udp_options" {
        for_each = try((egress_security_rules.value.options.udp != [] ? egress_security_rules.value.options.udp : []), [])
        content {
          #Optional
          max = udp_options.value.destination_port_range_max != null ? udp_options.value.destination_port_range_max : null
          min = udp_options.value.destination_port_range_min != null ? udp_options.value.destination_port_range_min : null
          dynamic "source_port_range" {
            for_each = try((udp_options.value.source_port_range_min != null || udp_options.value.source_port_range_max != null != [] ? egress_security_rules.value.options.udp : []), [])
            content {
              #Required
              max = source_port_range.value.source_port_range_max != null ? source_port_range.value.source_port_range_max : null
              min = source_port_range.value.source_port_range_min != null ? source_port_range.value.source_port_range_min : null
            }
          }
        }
      }
    }
  }
}