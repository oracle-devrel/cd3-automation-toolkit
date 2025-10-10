# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
