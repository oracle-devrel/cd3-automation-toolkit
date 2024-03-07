variable "compartment_id" {
   type = string
  default = null
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

variable "ipv4address" {
  type = string
  default = null
}

variable "urllist_name" {
  type = string
  default = null
}
variable "pattern" {
  type = string
  default = null
}
variable "urls_details" {
  type    = list(any)
  default = []
}

variable "icmp_type" {
  type = number
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
  default = null
}

variable "type" {
  type    = string
  default = null
}

variable "name" {
  type    = string
  default = null
}


variable "policy" {
  type    = map(any)
  default = {}
}

variable "service_port_ranges" {
  type    = map(any)
  default = {}
}

variable "key_name" {
  type    = string
  default = null
}




