// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Database
# Create Database Db Home
############################

#Required
variable "compartment_id" {
  type    = string
  default = null
}
variable "admin_password" {
  description = ""
  type        = string
  default     = null
}
variable "custom_database_image_name" {
  description = "DB image to be used for database"
  type        = string
  default     = null
}
variable "db_name" {
  description = ""
  type        = string
  default     = null
}

variable "db_workload" {
  description = ""
  type        = string
  default     = null
}

variable "defined_tags" {
  description = ""
  type        = map(any)
  default     = {}
}
variable "recovery_window_in_days" {
  description = ""
  type        = number
  default     = null
}
variable "freeform_tags" {
  description = ""
  type        = map(any)
  default     = null
}
variable "ncharacter_set" {
  description = ""
  type        = string
  default     = null
}
variable "pdbname" {
  description = ""
  type        = string
  default     = null
}
#variable "sid_prefix" {
#  description = ""
#  type        = string
#  default     = null
#}
variable "tde_wallet_password" {
  description = ""
  type        = string
  default     = null
}
variable "timestamp_for_point_in_time_recovery" {
  description = ""
  type        = string
  default     = null
}
variable "display_name" {
  description = ""
  type        = string
  default     = null
}
variable "db_source" {
  description = ""
  type        = string
  default     = null
}

#########
#Optional
#########
variable "backup_id" {
  description = ""
  type        = string
  default     = null
}
variable "backup_tde_password" {
  description = ""
  type        = string
  default     = null
}
variable "character_set" {
  description = ""
  type        = string
  default     = null
}
variable "database_id" {
  description = ""
  type        = string
  default     = null
}
#variable "db_home_db_software_image_id" {
#  description = ""
#  type        = string
#  default     = null
#}
variable "db_version" {
  description = ""
  type        = string
  default     = null
}
variable "auto_backup_enabled" {
  description = ""
  type        = bool
  default     = null
}
variable "auto_backup_window" {
  description = ""
  type        = string
  default     = null
}
variable "backup_dest_id" {
  description = ""
  type        = string
  default     = null
}
variable "backup_dest_type" {
  description = ""
  type        = string
  default     = null
}
variable "db_system_id" {
  description = ""
  type        = string
  default     = null
}
variable "is_desupported_version" {
  description = ""
  type        = bool
  default     = null
}
variable "kms_key_id" {
  description = ""
  type        = string
  default     = null
}
variable "kms_key_version_id" {
  description = ""
  type        = string
  default     = null
}
variable "vm_cluster_id" {
  description = ""
  type        = string
  default     = null
}
#variable "exadata_infra_name" {
#  type    = string
#  default = null
#}


