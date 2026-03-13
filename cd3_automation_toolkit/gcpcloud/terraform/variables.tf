# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
#
# Variables Block
# GCP OCI
#
############################

variable "credentials" {
  description = "path to private key jspn file"
  type        = string
}


###############################
# Oracle ExaInfra @GCP ########
###############################

variable "gcp_oci_exa_infra" {
  description = "Map of Exadata Infrastructure configurations."
  type = map(object({
    location                        = string
    gcp_oracle_zone                 = string
    project                         = string
    cloud_exadata_infrastructure_id = string
    display_name                    = string
    shape                           = string
    compute_count                   = number
    storage_count                   = number
    email                           = optional(string)

    # Maintenance Window
    maintenance_window = optional(object({
      patching_mode                    = optional(string, "ROLLING")
      preference                       = optional(string, "NO_PREFERENCE")
      is_custom_action_timeout_enabled = optional(bool, false)
      custom_action_timeout_mins       = optional(number, 15)
      days_of_week                     = optional(list(string), null)
      hours_of_day                     = optional(list(number), null)
      lead_time_week                   = optional(number, null)
      months                           = optional(list(string), null)
      weeks_of_month                   = optional(list(number), null)
    }), {})

    total_storage_size_gb = optional(string)
    # labels
    labels = optional(map(string), {})
  }))
}

###############################
# Oracle ExaVM Cluster @GCP
###############################

variable "gcp_oci_exa_vmclusters" {
  description = "Map of VM Cluster configurations"
  type = map(object({
    # MANDATORY
    location = string
    project  = string

    exadata_infrastructure_id   = string
    create_odb_network          = bool
    vpc_network_name            = optional(string)
    odb_network_gcp_oracle_zone = optional(string)
    client_subnet_cidr          = optional(string)
    backup_subnet_cidr          = optional(string)
    odb_network_id              = string
    odb_client_subnet_id        = string
    odb_backup_subnet_id        = string

    display_name            = string
    cloud_vm_cluster_id     = string
    cluster_name            = string
    gi_version              = string
    hostname_prefix         = string
    cpu_core_count          = number
    memory_size_gb          = number
    data_storage_size_tb    = number
    db_node_storage_size_gb = number
    node_count              = optional(number)
    ocpu_count              = optional(number)
    disk_redundancy         = optional(string)
    ssh_public_keys         = list(string)


    # OPTIONAL
    license_type           = string
    time_zone              = string
    scan_listener_port_tcp = number
    diagnostics_data_collection_options = object({
      diagnostics_events_enabled = bool
      health_monitoring_enabled  = bool
      incident_logs_enabled      = bool
    })
    timeout_create = string
    timeout_update = string
    timeout_delete = string

    # IMMUTABLE
    local_backup_enabled     = bool
    sparse_diskgroup_enabled = bool

    # TAGS
    labels = map(string)
  }))
}
