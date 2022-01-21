// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Networking
# Create Security List
############################

variable "compartment_id" {
	type = string
	default = null
}

variable "index" {
	type = number
	default = null
}

variable "vcn_id" {
	type = string
	default = null
}

variable "defined_tags" {
  type    = map
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
              "Oracle-Tags.CreatedBy"= "$${iam.principal.name}"
            }
}

variable "seclist_details" {
  type = list(object({
    display_name      = string
    vcn_name = string
    compartment_name = string
    freeform_tags = map(any)
    defined_tags = map(any)
    ingress_sec_rules = list(any)
    egress_sec_rules = list(any)
  }))
}

variable "display_name" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map
  default = {}
}

variable "egress_security_rules_destination" {
	type = string
	default = null
}

variable "egress_security_rules_protocol" {
	type = string
	default = null
}

variable "egress_security_rules_description" {
	type = string
	default = null
}

variable "egress_security_rules_destination_type" {
	type = string
	default = null
}

variable "egress_security_rules_icmp_options_type" {
	type = string
	default = null
}

variable "egress_security_rules_icmp_options_code" {
	type = number
	default = null
}

variable "egress_security_rules_stateless" {
	type = bool
	default = false
}

variable "egress_security_rules_tcp_options_destination_port_range_max" {
	type = number
	default = null
}

variable "egress_security_rules_tcp_options_destination_port_range_min" {
	type = number
	default = null
}

variable "egress_security_rules_tcp_options_source_port_range_max" {
	type = number
	default = null
}

variable "egress_security_rules_tcp_options_source_port_range_min" {
	type = number
	default = null
}
variable "egress_security_rules_udp_options_destination_port_range_max" {
	type = number
	default = null
}

variable "egress_security_rules_udp_options_destination_port_range_min" {
	type = number
	default = null
}
variable "egress_security_rules_udp_options_source_port_range_max" {
	type = number
	default = null
}

variable "egress_security_rules_udp_options_source_port_range_min" {
	type = number
	default = null
}

variable "ingress_security_rules_source" {
	type = string
	default = null
}

variable "ingress_security_rules_protocol" {
	type = string
	default = null
}

variable "ingress_security_rules_description" {
	type = string
	default = null
}

variable "ingress_security_rules_source_type" {
	type = string
	default = null
}

variable "ingress_security_rules_icmp_options_type" {
	type = string
	default = null
}

variable "ingress_security_rules_icmp_options_code" {
	type = number
	default = null
}

variable "ingress_security_rules_stateless" {
	type = bool
	default = false
}

variable "ingress_security_rules_tcp_options_destination_port_range_max" {
	type = number
	default = null
}

variable "ingress_security_rules_tcp_options_destination_port_range_min" {
	type = number
	default = null
}

variable "ingress_security_rules_tcp_options_source_port_range_max" {
	type = number
	default = null
}

variable "ingress_security_rules_tcp_options_source_port_range_min" {
	type = number
	default = null
}
variable "ingress_security_rules_udp_options_destination_port_range_max" {
	type = number
	default = null
}

variable "ingress_security_rules_udp_options_destination_port_range_min" {
	type = number
	default = null
}
variable "ingress_security_rules_udp_options_source_port_range_max" {
	type = number
	default = null
}

variable "ingress_security_rules_udp_options_source_port_range_min" {
	type = number
	default = null
}