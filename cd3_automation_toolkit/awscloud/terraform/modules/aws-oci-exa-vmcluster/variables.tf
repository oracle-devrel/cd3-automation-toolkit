# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################################
## Variables Block - Oracle ExaVM Cluster @AWS
## Create Oracle ExaVM Cluster @AWS
#################################################

variable "cluster_key" {
  type = string
}

variable "tags" {
  description = "A mapping of tags which should be assigned to the Cloud VM Cluster."
  type        = map(string)
  default     = null
}

variable "cluster_config" {
  type = object({
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
    tags = optional(map(string), {})
  })
}