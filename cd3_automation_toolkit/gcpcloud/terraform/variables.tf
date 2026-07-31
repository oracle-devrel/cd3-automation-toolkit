# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
#
# Variables Block
# GCP OCI
#
############################
variable "gcp_oci_adb" {

  description = "Map of ADB configurations."
  type = map(object({
    location                        = string
    project                         = string
    autonomous_database_id          = string
    database                        = string
    display_name                    = string
    admin_password                  = string

    create_odb_network          = optional(bool,false)
    create_odb_network_subnets  = optional(bool,false)
    odb_network_project         = optional(string)
    vpc_network_name            = optional(string)
    odb_network_gcp_oracle_zone = optional(string)
    client_subnet_cidr          = optional(string)
    odb_network_id              = optional(string)
    odb_client_subnet_id        = optional(string)

    compute_count                   = number
    cpu_core_count                  = optional(number)
    data_storage_size_tb            = optional(number)
    data_storage_size_gb            = optional(number)
    db_version                      = string
    db_workload                     = string
    db_edition                      = string
    n_character_set                 = optional(string)
    character_set                   = optional(string)
    license_type                    = string

    private_endpoint_ip             = optional(string)
    private_endpoint_label          = optional(string)

    is_auto_scaling_enabled         = optional(bool, false)
    is_storage_auto_scaling_enabled = optional(bool, false)

    maintenance_schedule_type       = optional(string)
    mtls_connection_required        = optional(string)
    backup_retention_period_days    = optional(number)
    email                           = optional(string)
    labels = optional(map(string), {})
  }))
  default = {}
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
  default = {}
}

###############################
# Oracle ExaVM Cluster @GCP
###############################

variable "gcp_oci_exa_vmclusters" {
  description = "Map of GCP VM Cluster configurations"
  type = map(object({
    # MANDATORY
    location                       = string
    project                        = string
    exadata_infrastructure_project = string

    exadata_infrastructure_id   = string
    odb_network_project         = string
    create_odb_network          = bool
    create_odb_network_subnets  = bool
    vpc_network_name            = optional(string)
    odb_network_gcp_oracle_zone = optional(string)
    client_subnet_cidr          = optional(string)
    backup_subnet_cidr          = optional(string)
    odb_network_id              = string
    odb_client_subnet_id        = string
    odb_backup_subnet_id        = string

    display_name        = string
    cloud_vm_cluster_id = string
    cluster_name        = optional(string)
    gi_version          = string
    hostname_prefix     = string

    cpu_core_count          = number
    memory_size_gb          = number
    data_storage_size_tb    = number
    db_node_storage_size_gb = number

    node_count      = optional(number)
    ocpu_count      = optional(number)
    disk_redundancy = optional(string)
    ssh_public_keys = list(string)

    # OPTIONAL
    license_type               = string
    time_zone                  = optional(string)
    scan_listener_port_tcp     = optional(number)
    scan_listener_port_tcp_ssl = optional(number)
    diagnostics_data_collection_options = optional(object({
      diagnostics_events_enabled = bool
      health_monitoring_enabled  = bool
      incident_logs_enabled      = bool
    }))
    timeout_create = optional(string)
    timeout_update = optional(string)
    timeout_delete = optional(string)

    # IMMUTABLE
    local_backup_enabled     = bool
    sparse_diskgroup_enabled = bool

    # TAGS
    labels = optional(map(string), {})
  }))
  default = {}
}
