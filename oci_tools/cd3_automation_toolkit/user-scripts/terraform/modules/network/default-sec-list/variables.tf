// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create Default Security List
############################

variable "manage_default_resource_id" {
  type    = string
  default = null
}

variable "key_name" {
  type    = string
  default = null
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "seclist_details" {
  type = map(any)
}

variable "display_name" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "egress_security_rules_destination" {
  type    = string
  default = null
}

variable "egress_security_rules_protocol" {
  type    = string
  default = null
}

variable "egress_security_rules_description" {
  type    = string
  default = null
}

variable "egress_security_rules_destination_type" {
  type    = string
  default = null
}

variable "egress_security_rules_icmp_options_type" {
  type    = string
  default = null
}

variable "egress_security_rules_icmp_options_code" {
  type    = number
  default = null
}

variable "egress_security_rules_stateless" {
  type    = bool
  default = false
}

variable "egress_security_rules_tcp_options_destination_port_range_max" {
  type    = number
  default = null
}

variable "egress_security_rules_tcp_options_destination_port_range_min" {
  type    = number
  default = null
}

variable "egress_security_rules_tcp_options_source_port_range_max" {
  type    = number
  default = null
}

variable "egress_security_rules_tcp_options_source_port_range_min" {
  type    = number
  default = null
}
variable "egress_security_rules_udp_options_destination_port_range_max" {
  type    = number
  default = null
}

variable "egress_security_rules_udp_options_destination_port_range_min" {
  type    = number
  default = null
}
variable "egress_security_rules_udp_options_source_port_range_max" {
  type    = number
  default = null
}

variable "egress_security_rules_udp_options_source_port_range_min" {
  type    = number
  default = null
}

variable "ingress_security_rules_source" {
  type    = string
  default = null
}

variable "ingress_security_rules_protocol" {
  type    = string
  default = null
}

variable "ingress_security_rules_description" {
  type    = string
  default = null
}

variable "ingress_security_rules_source_type" {
  type    = string
  default = null
}

variable "ingress_security_rules_icmp_options_type" {
  type    = string
  default = null
}

variable "ingress_security_rules_icmp_options_code" {
  type    = number
  default = null
}

variable "ingress_security_rules_stateless" {
  type    = bool
  default = false
}

variable "ingress_security_rules_tcp_options_destination_port_range_max" {
  type    = number
  default = null
}

variable "ingress_security_rules_tcp_options_destination_port_range_min" {
  type    = number
  default = null
}

variable "ingress_security_rules_tcp_options_source_port_range_max" {
  type    = number
  default = null
}

variable "ingress_security_rules_tcp_options_source_port_range_min" {
  type    = number
  default = null
}
variable "ingress_security_rules_udp_options_destination_port_range_max" {
  type    = number
  default = null
}

variable "ingress_security_rules_udp_options_destination_port_range_min" {
  type    = number
  default = null
}
variable "ingress_security_rules_udp_options_source_port_range_max" {
  type    = number
  default = null
}

variable "ingress_security_rules_udp_options_source_port_range_min" {
  type    = number
  default = null
}