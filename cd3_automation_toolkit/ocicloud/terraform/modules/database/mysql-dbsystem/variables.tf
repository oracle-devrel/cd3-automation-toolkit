# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Database
# Create MySQL DB Systems
############################

variable "compartment_id" {
  description = "The OCID of the compartment where the MySQL DB system will be created."
  type        = string
}

variable "display_name" {
  description = "The display name of the MySQL DB system."
  type        = string
}

variable "configuration_compartment_id" {
  description = "The OCID of the compartment where the MySQL configuration is located."
  type        = string
}

variable "configuration_id" {
  description = "The OCID or name of the MySQL configuration."
  type        = string
}

variable "shape_name" {
  description = "The shape of the MySQL DB system."
  type        = string
}

variable "admin_username" {
  description = "The admin username for the MySQL DB system."
  type        = string
}

variable "admin_password" {
  description = "The admin password for the MySQL DB system."
  type        = string
  sensitive   = true
}

variable "availability_domain" {
  description = "The availability domain where the MySQL DB system will be created."
  type        = string
}

variable "subnet_id" {
  description = "The OCID of the subnet where the MySQL DB system will be created."
  type        = string
}

variable "hostname_label" {
  description = "The hostname label of the MySQL DB system."
  type        = string
}

variable "data_storage_size_in_gb" {
  description = "value to be used for data_storage_size_in_gbs"
}

variable "source_type" {
  description = "Source type"
  type        = string
}

variable "is_highly_available" {
  description = "Is highly available"
  type        = bool
}

variable "maintenance_window_start_time" {
  description = "Maintenance window start time"
  type        = string
}

variable "port" {
  description = "Port"
  type        = number
}

variable "port_x" {
  description = "X protocol port"
  type        = number
}

variable "backup_id" {
  description = "Backup ID for the MySQL DB System"
  type        = string
}

variable "database_management" {
  description = "Database management"
  type        = string
}

variable "deletion_policy_automatic_backup_retention" {
  description = "Automatic backup retention on deletion"
  type        = string
}

variable "deletion_policy_final_backup" {
  description = "Final backup on deletion"
  type        = string
}

variable "deletion_policy_is_delete_protected" {
  description = "Is delete protected"
  type        = bool
}

variable "description" {
  description = "Description for the MySQL DB System"
  type        = string
}

variable "fault_domain" {
  description = "Fault domain"
  type        = string
}

variable "ip_address" {
  description = "IP address"
  type        = string
}

variable "backup_policy_is_enabled" {
  description = "Is backup policy enabled"
  type        = bool
}

variable "pitr_policy_is_enabled" {
  description = "Is point-in-time recovery enabled"
  type        = bool
}

variable "backup_policy_retention_in_days" {
  description = "Backup retention in days"
  type        = number
}

variable "backup_policy_window_start_time" {
  description = "Backup window start time"
  type        = string
}

variable "vcn_names" {
  type    = list(any)
  default = []
}

variable "crash_recovery" {
  description = "Crash recovery"
  type        = string
}

variable "network_compartment_id" {
  description = "Network compartment OCID to fetch NSG/Subnet details"
  type        = string
  default     = null
}

variable "compartment_ocids" {
  type    = string
  default = null
}

variable "defined_tags" {
  type = map(any)
  default = null
}

variable "freeform_tags" {
  type = map(any)
  default = null
}