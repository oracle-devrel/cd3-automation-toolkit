# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
variable "compartment_id" {
   type = string
  default = null
}
variable "app_group_name" {
  type = string
  default = null
}
variable "apps" {
  type = list(string)
  default = []
}
variable "subnet_name" {
  type = string
  default = null
}
variable "vcn_name" {
  type = string
  default = null
}
variable "network_firewall_policy_id" {
  type = string
  default = null
}

variable "display_name" {
  type = string
  default = null
}

variable "address_list_name" {
  type = string
  default = null
}
variable "address_type" {
  type = string
  default = null
}
variable "addresses" {
  type    = list(string)
  default = []
}

variable "ipv4address" {
  type = string
  default = null
}

variable "icmp_type" {
  type = number
  default = null

}
variable "app_type" {
  type = string
  default = null

}
variable "app_list_name" {
  type = string
  default = null

}

variable "icmp_code" {
  type = number
  default = null
}
variable "minimum_port" {
  type = number
  default = null
}

variable "maximum_port" {
  type = number
  default = null
}

variable "service_name" {
   type = string
  default = null
}

variable "service" {
   type = string
  default = null
}

variable "service_type" {
   type = string
  default = null
}

variable "region" {
  type    = string
  default = "us-ashburn-1"
}

variable "type" {
  type    = string
  default = null
}

variable "name" {
  type    = string
  default = null
}

variable "secret_name" {
  type = string
  default = null
}
variable "secret_source" {
  type = string
  default = null
}
variable "secret_type" {
  type = string
  default = null
}
variable "vault_secret_id" {
  type = string
  default = null
}
variable "version_number" {
  type = string
  default = null
}

variable "are_certificate_extensions_restricted" {
  type = bool
  default = "true"
}
variable "is_auto_include_alt_name" {
  type = bool
  default = "true"
}
variable "is_expired_certificate_blocked" {
  type = bool
  default = "true"
}
variable "is_out_of_capacity_blocked" {
  type = bool
}
variable "is_revocation_status_timeout_blocked" {
  type = bool
}
variable "is_unknown_revocation_status_blocked" {
  type = bool
  default = "true"
}
variable "is_unsupported_cipher_blocked" {
  type = bool
  default = "true"
}
variable "is_unsupported_version_blocked" {
  type = bool
  default = "true"
}
variable "is_untrusted_issuer_blocked" {
  type = bool
  default = "true"
}

variable "profile_name" {
  type = string
  default = null
}

variable "profile_type" {
  type = string
  default = null
}



