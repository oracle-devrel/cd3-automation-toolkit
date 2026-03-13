# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
#
# Variables Block
# AWS OCI
#
############################

# ============================
# Mandatory: AWS Authentication
# ============================

variable "aws_region" {
  description = "AWS region for provider configuration"
  type        = string
  default     = "us-west-2"
}

variable "aws_access_key" {
  description = "AWS Access Key ID (use environment variable TF_VAR_aws_access_key)"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Access Key (use environment variable TF_VAR_aws_secret_key)"
  type        = string
  sensitive   = true
}

###############################
# Oracle ExaInfra @AWS ######
###############################

variable "aws_oci_exa_infra" {
  description = "Map of Exadata Infrastructure configurations."
  type = map(object({
    environment          = string
    region               = string
    availability_zone    = string
    availability_zone_id = string
    display_name         = string
    shape                = string
    compute_count        = number
    storage_count        = number
    database_server_type = string
    storage_server_type  = string
    customer_contacts    = list(object({ email = string }))

    # Maintenance Window
    maintenance_window = optional(object({
      patching_mode                    = optional(string, "ROLLING")
      preference                       = optional(string, "NO_PREFERENCE")
      is_custom_action_timeout_enabled = optional(bool, false)
      custom_action_timeout_in_mins    = optional(number, 15)
      days_of_week                     = optional(list(string), null)
      hours_of_day                     = optional(list(number), null)
      lead_time_in_weeks               = optional(number, null)
      months                           = optional(list(string), null)
      weeks_of_month                   = optional(list(number), null)
    }), {})

    # Tags
    tags = optional(map(string), {})
  }))
}


###############################
# Oracle ExaVM Cluster @AWS ###
###############################

variable "aws_oci_exa_vmclusters" {
  description = "Map of VM Cluster configurations"
  type = map(object({
    # MANDATORY
    environment                 = string
    region                      = string
    exadata_infrastructure_name = string
    odb_network_name            = string
    display_name                = string
    cluster_name                = string
    gi_version                  = string
    hostname_prefix             = string
    cpu_core_count              = number
    memory_size_in_gbs          = number
    data_storage_size_in_tbs    = number
    db_node_storage_size_in_gbs = number
    ssh_public_keys             = list(string)

    # OPTIONAL
    license_model          = string
    timezone               = string
    scan_listener_port_tcp = number
    data_collection_options = object({
      is_diagnostics_events_enabled = bool
      is_health_monitoring_enabled  = bool
      is_incident_logs_enabled      = bool
    })
    timeout_create = string
    timeout_update = string
    timeout_delete = string

    # IMMUTABLE
    is_local_backup_enabled     = bool
    is_sparse_diskgroup_enabled = bool

    # TAGS
    tags = map(string)
  }))
}