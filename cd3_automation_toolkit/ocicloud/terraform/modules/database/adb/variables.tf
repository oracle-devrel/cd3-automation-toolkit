# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Autonomous database
## Create autonomous database
#################################

variable "admin_password" {
  description = "Password for the admins"
  type        = string
}

variable "character_set" {
  type = string
}

variable "customer_contacts" {
  description = "The customer_contacts of ADB"
  type        = list(string)

}

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "database_edition" {
  description = "The database edition of ADB"
  type        = string
}

variable "data_storage_size_in_tbs" {
  description = "Data storage size for the DB"
  type        = number
}

variable "db_name" {
  description = "Name of the database"
  type        = string
}

variable "freeform_tags" {
  description = "Free-form tags for the DB"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the DB"
  type        = map(string)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "display_name" {
  description = "User-friendly name to the autonomous database"
  type        = string
}

variable "db_version" {
  description = "the version of DB"
  type        = string
}


variable "db_workload" {
  description = "The type of autonomous database-ATP or ADW"
  type        = string
}

variable "license_model" {
  description = "The license model for ADB"
  type        = string

}

variable "ncharacter_set" {
  description = "The ncharacter set of ADB"
  type        = string

}

variable "network_compartment_id" {
  description = "The network compartment of the subnet"
  type        = string
  default     = ""
}

variable "network_security_group_ids" {
  description = "NSGs to be attahced to ADB"
  type        = any
  default     = ""
}

variable "subnet_id" {
  description = "The subnet name into which the ADB will be launched"
  type        = string
  default     = ""
}

variable "vcn_id" {
  type    = string
  default = ""
}

variable "whitelisted_ips" {
  type    = list(string)
  default = []
}
variable "are_primary_whitelisted_ips_used" {
  default = null
}
variable "auto_refresh_frequency_in_seconds" {
  default = null
}
variable "auto_refresh_point_lag_in_seconds" {
  default = null
}
variable "autonomous_container_database_id" {
  default = null
}
variable "adb_source" {
    default = null
}
variable "source_id" {
  default = null
}
variable "autonomous_database_source_backup_id" {
  default = null
}
variable "autonomous_database_id" {
  default = null
}

variable "autonomous_maintenance_schedule_type" {
  default = null
}
variable "backup_retention_period_in_days" {
  default = null
}
variable "compute_count" {
  default = null
}
variable "compute_model" {
  default = null
}
variable "data_safe_status" {
  default = null
}
variable "data_storage_size_in_gb" {
  default = null
}
variable "disaster_recovery_type" {
  default = null
}
variable "in_memory_percentage" {
  default = null
}
variable "kms_key_id" {
  default = null
}
variable "vault_id" {
  default = null
}
variable "is_auto_scaling_enabled" {
  default = null
}
variable "is_auto_scaling_for_storage_enabled" {
  default = null
}
variable "is_backup_retention_locked" {
  default = null
}
variable "is_dedicated" {
  default = null
}
variable "is_local_data_guard_enabled" {
  default = null
}
variable "is_mtls_connection_required" {
  default = null
}
variable "is_replicate_automatic_backups" {
  default = null
}

variable "ocpu_count" {
  default = null
}
variable "private_endpoint_ip" {
  default = null
}
variable "private_endpoint_label" {
  default = null
}
variable "refreshable_mode" {
  default = null
}
variable "remote_disaster_recovery_type" {
  default = null
}
variable "secret_id" {
  default = null
}
variable "secret_version_number" {
  default = null
}

variable "standby_whitelisted_ips" {
  default = null
}
variable "subscription_id" {
  default = null
}
variable "time_of_auto_refresh_start" {
  default = null
}
variable "timestamp" {
  default = null
}
variable "use_latest_available_backup_time_stamp" {
  default = null
}
