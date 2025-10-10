# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Database
# Create Database VM BM
############################


variable "availability_domain" {
  type    = string
  default = null
}
variable "compartment_id" {
  type    = string
  default = ""
}
variable "hostname" {
  type    = string
  default = ""
}
variable "vcn_names" {
  type    = list(any)
  default = []
}
variable "network_compartment_id" {
  type    = string
  default = ""
}
variable "shape" {
  type    = string
  default = ""
}
variable "ssh_public_keys" {
  type    = list(any)
  default = []
}
variable "subnet_id" {
  type    = string
  default = ""
}
variable "node_count" {
  type = number
}
variable "nsg_ids" {
  type    = list(string)
  default = []
}

variable "time_zone" {
  type    = string
  default = ""
}

variable "cpu_core_count" {
  type    = number
  default = null
}

variable "database_edition" {
  type    = string
  default = ""
}

variable "data_storage_size_in_gb" {
  type    = number
  default = null

}
variable "data_storage_percentage" {
  type    = number
  default = null
}

variable "disk_redundancy" {
  type    = string
  default = ""
}
variable "license_model" {
  type    = string
  default = ""
}
variable "display_name" {
  type    = string
  default = ""
}

variable "db_version" {
  type    = string
  default = ""
}
variable "pdb_name" {
  type    = string
  default = ""
}
variable "db_name" {
  type    = string
  default = null
}
variable "db_home_display_name" {
  type    = string
  default = null
}
variable "admin_password" {
  type    = string
  default = ""
}

variable "db_workload" {
  type    = string
  default = ""
}
variable "auto_backup_enabled" {
  type    = bool
  default = null
}
variable "ncharacter_set" {
  type    = string
  default = ""
}
variable "character_set" {
  type    = string
  default = ""
}
variable "recovery_window_in_days" {
  type    = number
  default = null
}

variable "defined_tags" {
  type    = map(any)
  default = {}
}
variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "cluster_name" {
  type    = string
  default = ""
}