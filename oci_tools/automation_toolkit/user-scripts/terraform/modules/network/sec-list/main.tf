// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Networking
# Create Security List
############################

resource "oci_core_security_list" "security_list" {

    #Required
    count = (var.display_name != null  && var.display_name != "") ? 1 : 0
    compartment_id = var.compartment_id
    vcn_id         = var.vcn_id

    #Optional
    defined_tags   = var.defined_tags
    display_name   = var.display_name
    freeform_tags  = var.freeform_tags

    dynamic "ingress_security_rules" {
        for_each = lookup(var.seclist_details[var.index], "ingress_sec_rules")

        content {
          #Required
          protocol    = ingress_security_rules.value["protocol"]
          source      = ingress_security_rules.value["source"]

          #Optional
          description = ingress_security_rules.value["description"]
          dynamic "icmp_options" {
              for_each = ingress_security_rules.value["icmp_options"] != [] ? ingress_security_rules.value["icmp_options"] : []
              content {
                  #Required
                  type = ingress_security_rules.value["icmp_options"][0].icmp_options_type

                  #Optional
                  code = ingress_security_rules.value["icmp_options"][0].icmp_options_code != null ? ingress_security_rules.value["icmp_options"][0].icmp_options_code : null
              }
          }

          source_type = ingress_security_rules.value["source_type"] != null ? ingress_security_rules.value["source_type"] : null
          stateless   = ingress_security_rules.value["stateless"]

          dynamic "tcp_options" {
              for_each = ingress_security_rules.value["tcp_options"] != [] ? ingress_security_rules.value["tcp_options"] : []
              content {
                    min = ingress_security_rules.value["tcp_options"][0].tcp_options_destination_port_min != null ? ingress_security_rules.value["tcp_options"][0].tcp_options_destination_port_min : null
                    max = ingress_security_rules.value["tcp_options"][0].tcp_options_destination_port_max != null ? ingress_security_rules.value["tcp_options"][0].tcp_options_destination_port_max : null
                    dynamic "source_port_range" {
                        for_each = ingress_security_rules.value["tcp_source_ports"] != [] ? ingress_security_rules.value["tcp_source_ports"] : []
                        content {
                        #Required
                        max = ingress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_max != null ? ingress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_max : null
                        min = ingress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_min != null ? ingress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_min : null
                        }
                    }
                  }
          }
          dynamic "udp_options" {
                for_each = ingress_security_rules.value["udp_options"] != [] ? ingress_security_rules.value["udp_options"] : []
                content {
                    #Optional
                    max = ingress_security_rules.value["udp_options"][0].udp_options_destination_port_range_max != null ? ingress_security_rules.value["udp_options"][0].udp_options_destination_port_range_max : null
                    min = ingress_security_rules.value["udp_options"][0].udp_options_destination_port_range_min != null ? ingress_security_rules.value["udp_options"][0].udp_options_destination_port_range_min : null
                    dynamic "source_port_range" {
                        for_each = ingress_security_rules.value["udp_source_ports"] != [] ? ingress_security_rules.value["udp_source_ports"] : []
                        content {
                        #Required
                        max = ingress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_max != null ? ingress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_max : null
                        min = ingress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_min != null ? ingress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_min : null
                        }
                    }
                }
            }
        }
      }

    dynamic "egress_security_rules" {
        for_each = lookup(var.seclist_details[var.index], "egress_sec_rules")

        content {
          #Required
          protocol    = egress_security_rules.value["protocol"]
          destination      = egress_security_rules.value["destination"]

          #Optional
          description = egress_security_rules.value["description"]
          dynamic "icmp_options" {
              for_each = egress_security_rules.value["icmp_options"] != [] ? egress_security_rules.value["icmp_options"] : []
              content {
                  #Required
                  type = egress_security_rules.value["icmp_options"][0].icmp_options_type

                  #Optional
                  code = egress_security_rules.value["icmp_options"][0].icmp_options_code != null ? egress_security_rules.value["icmp_options"][0].icmp_options_code : null
              }
          }
          
          destination_type = egress_security_rules.value["destination_type"] != null ? egress_security_rules.value["destination_type"] : null
          stateless   = egress_security_rules.value["stateless"]

          dynamic "tcp_options" {
              for_each = egress_security_rules.value["tcp_options"] != [] ? egress_security_rules.value["tcp_options"] : []
              content {
                    min = egress_security_rules.value["tcp_options"][0].tcp_options_destination_port_min != null ? egress_security_rules.value["tcp_options"][0].tcp_options_destination_port_min : null
                    max = egress_security_rules.value["tcp_options"][0].tcp_options_destination_port_max != null ? egress_security_rules.value["tcp_options"][0].tcp_options_destination_port_max : null
                    dynamic "source_port_range" {
                        for_each = egress_security_rules.value["tcp_source_ports"] != [] ? egress_security_rules.value["tcp_source_ports"] : []
                        content {
                        #Required
                        max = egress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_max != null ? egress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_max : null
                        min = egress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_min != null ? egress_security_rules.value["tcp_source_ports"][0].tcp_options_source_port_range_min : null
                        } 
                      }
                  }
          }
          dynamic "udp_options" {
                for_each = egress_security_rules.value["udp_options"] != [] ? egress_security_rules.value["udp_options"] : []
                content {
                    #Optional
                    max = egress_security_rules.value["udp_options"][0].udp_options_destination_port_range_max != null ? egress_security_rules.value["udp_options"][0].udp_options_destination_port_range_max : null
                    min = egress_security_rules.value["udp_options"][0].udp_options_destination_port_range_min != null ? egress_security_rules.value["udp_options"][0].udp_options_destination_port_range_min : null
                    dynamic "source_port_range" {
                        for_each = egress_security_rules.value["udp_source_ports"] != [] ? egress_security_rules.value["udp_source_ports"] : []
                        content {
                        #Required
                        max = egress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_max != null ? egress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_max : null
                        min = egress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_min != null ? egress_security_rules.value["udp_source_ports"][0].udp_options_source_port_range_min : null
                        }
                    }
                }
            }
        }
      } 
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"]]
    }
}