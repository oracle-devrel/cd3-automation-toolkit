# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
#
# Variables Block
# Azure OCI
#
############################


###########################
###Oracle ADB @Azure ######
###########################

variable "az_oci_adb" {
  type = map(object({
    display_name                     = string
    az_region                        = string
    resource_group_name              = string
    network_resource_group_name      = string
    virtual_network_id               = string
    subnet_id                        = string
    db_workload                      = string
    mtls_connection_required         = bool
    backup_retention_period_in_days  = number
    compute_model                    = string
    data_storage_size_in_tbs         = number
    auto_scaling_for_storage_enabled = bool
    admin_password                   = string
    auto_scaling_enabled             = bool
    character_set                    = string
    compute_count                    = number
    ncharacter_set                   = string
    license_model                    = string
    db_version                       = string
    customer_contacts                = optional(list(string))
    common_tags                      = optional(map(string))
  }))
  default = {}
}


###########################
###Oracle ExaInfra @Azure ######
###########################

variable "az_oci_exa_infra" {
  type = map(object({
    display_name        = string
    az_region           = string
    az_zone = string
    resource_group_name = string

    compute_count        = number
    storage_count        = number
    shape                = string
    database_server_type = optional(string)
    storage_server_type  = optional(string)

    maintenance_window = object({
      patching_mode      = string
      preference         = string
      lead_time_in_weeks = optional(number)
      months             = optional(list(number))
      weeks_of_month     = optional(list(number))
      days_of_week       = optional(list(number))
      hours_of_day       = optional(list(number))
    })
    customer_contacts                = optional(list(string))
    common_tags = optional(map(string))

  }))
  default = {}
}


variable "az_oci_exa_vmclusters" {
  type = map(object({
    display_name                = string
    az_region                   = string
    resource_group_name         = string
    network_resource_group_name = string
    virtual_network_id          = string
    subnet_id                   = string
    exadata_infrastructure_name = string
    hostname                    = string
    cpu_core_count              = string
    gi_version                  = string
    license_model               = string
    ssh_public_keys             = list(string)
    gi_version                  = string
    backup_subnet_cidr          = optional(string)
    cluster_name                = optional(string)
    domain                      = optional(string)
    oci_zone_id                 = optional(string)
    diagnostics_events_enabled  = optional(bool)
    health_monitoring_enabled   = optional(bool)
    incident_logs_enabled       = optional(bool)
    data_storage_percentage     = optional(number)
    data_storage_size_in_tbs    = optional(number)
    db_node_storage_size_in_gbs = optional(number)
    local_backup_enabled        = optional(bool)
    sparse_diskgroup_enabled    = optional(bool)
    memory_size_in_gbs          = optional(number)
    scan_listener_port_tcp      = optional(number)
    scan_listener_port_tcp_ssl  = optional(number)
    system_version              = optional(string)
    time_zone                   = optional(string)
    mount_point                 = optional(string)
    size_in_gb                  = optional(number)
    common_tags = optional(map(string))


  }))
  default = {}
}

