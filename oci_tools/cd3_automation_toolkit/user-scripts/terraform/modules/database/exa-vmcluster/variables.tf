// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Database
# Create ExaVMClusters
############################
variable "backup_subnet_id" {
  type    = string
  default = ""
}
variable "cpu_core_count" {
  type = number
}
variable "display_name" {
  type    = string
  default = ""
}
variable "gi_version" {
  type    = string
  default = ""
}
variable "hostname" {
  type    = string
  default = ""
}
variable "ssh_public_keys" {
  type    = list(any)
  default = []
}
variable "cluster_subnet_id" {
  type    = string
  default = ""
}
variable "backup_network_nsg_ids" {
  type    = list(string)
  default = []
}
variable "cluster_name" {
  type    = string
  default = ""
}
variable "data_storage_percentage" {
  type = number
}
variable "defined_tags" {
  type    = map(string)
  default = {}
}
variable "domain" {
  type    = string
  default = ""
}
variable "freeform_tags" {
  type    = map(any)
  default = {}
}
variable "is_local_backup_enabled" {
  type    = bool
  default = false
}
variable "is_sparse_diskgroup_enabled" {
  type    = bool
  default = false
}
variable "license_model" {
  type    = string
  default = ""
}
variable "nsg_ids" {
  type    = list(string)
  default = []
}
variable "ocpu_count" {
  type = number
}
variable "scan_listener_port_tcp" {
  type    = number
  default = 1521
}
variable "scan_listener_port_tcp_ssl" {
  type    = number
  default = 2484
}
variable "time_zone" {
  type    = string
  default = ""
}
variable "compartment_id" {
  default = ""
}
variable "exadata_infrastructure_id" {
  default = ""
}