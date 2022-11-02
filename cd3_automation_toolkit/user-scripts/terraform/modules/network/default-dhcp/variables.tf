// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create Default DHCP Options
############################

variable "manage_default_resource_id" {
  type    = string
  default = null
}

variable "server_type" {
  type    = string
  default = null
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "custom_dns_servers" {
  type    = list(any)
  default = [""]
}

variable "search_domain_names" {
  type    = list(any)
  default = []
}