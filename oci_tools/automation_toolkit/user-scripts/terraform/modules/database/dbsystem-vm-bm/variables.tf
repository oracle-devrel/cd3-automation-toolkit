// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Database
# Create DBSystems-VM-BM
############################


variable "compartment_name" {
  type = string
  description = "The compartment ID where alarm is created."
  default = null
}

variable "db_system_display_name" {
  type = string
  description = "The name you assign to the DB System during creation."
  default = null
}

variable "ssh_key_var_name" {
  type = list
  default = null
}

variable "availability_domain" {
  type = string
  description = "availability_domain"
  default     = null
}

variable "cpu_core_count" {
  type = string
  default     = null
}

variable "database_edition" {
  type = string
  default     = null
}

variable "admin_password" {
  type = string
  default     = null
}

variable "db_name" {
  type = string
  default     = null
}

variable "character_set" {
  type = string
  default     = null
}

variable "ncharacter_set" {
  type = string
  default     = null
}

variable "db_workload" {
  type = string
  default     = null
}

variable "pdb_name" {
  type = string
  default     = null
}

variable "enable_automatic_backups" {
  type = string
  default     = null
}

variable "back_up_retention_period" {
  type = string
  default     = null
}

variable "db_version" {
  type = string
  default     = null
}

variable "disk_redundancy" {
  type = string
  default     = null
}

variable "shape" {
  type = string
  default     = null
}

variable "subnet_name" {
  type = string
  default     = null
}

variable "hostname" {
  type = string
  default     = null
}

variable "data_storage_size_in_gb" {
  type = string
  default     = null
}

variable "data_storage_percentage" {
  type = string
  default     = null
}

variable "license_model" {
  type = string
  default     = null
}

variable "node_count" {
  type = string
  default     = null
}

variable "time_zone" {
  type = string
  default     = null
}

variable "defined_tags" {
type = map
default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
            "Oracle-Tags.CreatedBy"= "$${iam.principal.name}"
          }
}

variable "freeform_tags" {
  type = map
  default = {}
}