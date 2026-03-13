# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

##############################
# Variables Block - Database CDB
# Create Databases
##############################
variable "compartment_id" {
  type    = string
  default = null
}
variable "db_home_id" {
  type    = string
  default = null
}

variable "vm_cluster_name" {
  type    = string
  default = null
}

variable "custom_database_image_name" {
  type    = string
  default = null
}


variable "database" {
  description = "List of database objects to create in the DB Home"
  type = list(object({
    db_name                   = string
    db_unique_name            = string
    admin_password            = optional(string)
    admin_secret_id           = optional(string)
    auto_backup_enabled       = optional(bool)
    auto_backup_window        = optional(string)
    recovery_window_in_days   = optional(number)
    character_set             = optional(string)
    ncharacter_set            = optional(string)
    sid_prefix                = optional(string)
    pdb_name                  = optional(string)
    backup_dest_type          = optional(string)
    backup_dest_id            = optional(string)
    auto_full_backup_day      = optional(string)
    run_immediate_full_backup = optional(string)
    backup_deletion_policy    = optional(string)
     auto_full_backup_window = optional(string)
    defined_tags              = optional(map(string), {})
    freeform_tags             = optional(map(string), {})
    tde_wallet_password       = optional(string)
    tde_wallet_secret_id      = optional(string)
    dbrs_policy_id            = optional(string)
  }))
  default = []
}

variable "db_source" {
  type    = string
  default = null
}
variable "db_version" {
  type    = string
  default = null
}

variable "exadata_infrastructure_comp_id" {
  description = ""
  type        = string
  default     = null
}
