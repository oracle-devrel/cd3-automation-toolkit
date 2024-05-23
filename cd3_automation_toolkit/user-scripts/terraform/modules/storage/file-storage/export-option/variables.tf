// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Storage
# Create Export Options
############################

variable "export_set_id" {
  type    = string
  default = null
}

variable "file_system_id" {
  type    = string
  default = null
}

variable "export_path" {
  type    = string
  default = null
}

variable "key_name" {
  type    = string
  default = null
}

variable "nfs_export_options" {
  type = map(any)
}
variable "is_idmap_groups_for_sys_auth" {
  type    = bool
  default = null
}
