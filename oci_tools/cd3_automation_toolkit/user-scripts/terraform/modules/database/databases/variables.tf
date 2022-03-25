// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Database
# Create Databases
############################
variable "compartment_id" {
  type    = string
  default = null
}
variable "db_home_name" {
  type = string
  default = null
}
variable "vm_cluster_name" {
  type = string
  default = null
}
variable "custom_database_image_name" {
  type = string
  default = null
}
variable "databases" {
  description = "Map of databases to provision inside existing db_home"
  type = list(object({
    admin_password                       = string,
    backup_id                            = string,
    backup_tde_password                  = string,
    db_unique_name                       = string,
    character_set                        = string,
    database_id                          = string,
    auto_backup_enabled                  = bool,
    auto_backup_window                   = string,
    backup_dest_id                       = string,
    backup_dest_type                     = string,
    recovery_window_in_days              = number,
    db_name                              = string,
    db_workload                          = string,
    defined_tags                         = map(string),
    freeform_tags                        = map(string),
    ncharacter_set                       = string,
    sid_prefix                           = string,
    pdb_name                             = string,
    tde_wallet_password                  = string,
    timestamp_for_point_in_time_recovery = string,
  }))
  default = [{
    admin_password                       = null
    backup_id                            = null
    backup_tde_password                  = null
    character_set                        = null
    db_unique_name                       = null
    database_id                          = null
    auto_backup_enabled                  = null
    auto_backup_window                   = null
    backup_dest_id                       = null
    backup_dest_type                     = null
    recovery_window_in_days              = null
    db_name                              = null
    db_workload                          = null
    defined_tags                         = {}
    freeform_tags                        = {}
    ncharacter_set                       = null
    sid_prefix                           = null
    pdb_name                             = null
    tde_wallet_password                  = null
    timestamp_for_point_in_time_recovery = null
  }]
}
variable "db_source" {
  type    = string
  default = null
}
variable "db_version" {
  type    = string
  default = null
}
variable "kms_key_id" {
  type    = string
  default = null
}
variable "kms_key_version_id" {
  type    = string
  default = null
}
