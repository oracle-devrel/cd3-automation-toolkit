// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Instance
# Create Instance
############################

variable "availability_domain" {
  type = string
  default = ""
}
variable "compartment_id" {
  type = string
  default = ""
}
variable "shape" {
  type = string
  description = "The shape of an instance."
  default = "VM.Standard2.1"
}
variable "ocpu_count" {
  type = number
  default = null
}
variable "dedicated_vm_host_name" {
  type = string
  default = null
}
variable "defined_tags" {
  type = map(any)
  default = {}
}
variable "display_name" {
  type = string
  default = null
}
variable "extended_metadata" {
  type = map(any)
  default = {}
}
variable "fault_domain" {
  type = string
  default = null
}
variable "freeform_tags" {
  type = map(any)
  default = {}
}
variable "ipxe_script" {
  type = string
  default = null
}
variable "is_pv_encryption_in_transit_enabled" {
  type = bool
  default = null
}
variable "ssh_public_keys" {
  type = string
  default = null
}
variable "preserve_boot_volume" {
  type = bool
  default = null
}
variable "assign_private_dns_record" {
  type = string
  default = null
}
variable "assign_public_ip" {
  type = bool
  default = null
}
variable "hostname_label" {
  type = string
  default = null
}
variable "nsg_ids" {
  type = list(string)
  default = []
}
variable "private_ip" {
  type = string
  default = null
}
variable "subnet_id" {
  type = string
  default = null
}
variable "vlan_id" {
  type = string
  default = null
}
variable "source_type" {
  type = string
  default = null
}
variable "source_image_id" {
  type = string
  default = null
}
variable "boot_volume_size_in_gbs" {
  type = number
  default = null
}
variable "kms_key_id" {
  type = string
  default = null
}