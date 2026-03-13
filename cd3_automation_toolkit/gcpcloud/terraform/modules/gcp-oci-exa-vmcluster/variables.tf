# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################################
## Variables Block - Oracle ExaVM Cluster @GCP
## Create Oracle ExaVM Cluster @GCP
#################################################

variable "labels" {
  description = "A mapping of tags which should be assigned to the Cloud Exadata Infrastructure."
  type        = map(string)
  default     = null
}

variable "db_server_ocids" {
  description = "DB Server OCIDs"
  type        = list(string)
  default     = null
}
variable "exadata_infrastructure_id" {
  description = "Cloud Exadata Infrastructure ID"
  type        = string
  default     = null
}

variable "cluster_config" {
  type = object({
    # MANDATORY
    location                    = string
    project                     = string
    exadata_infrastructure_id   = string
    create_odb_network          = bool
    vpc_network_name            = optional(string)
    odb_network_gcp_oracle_zone = optional(string)
    client_subnet_cidr          = optional(string)
    backup_subnet_cidr          = optional(string)
    odb_network_id              = string
    odb_client_subnet_id        = string
    odb_backup_subnet_id        = string
    display_name                = string
    cloud_vm_cluster_id         = string
    cluster_name                = string
    gi_version                  = string
    hostname_prefix             = string
    cpu_core_count              = number
    memory_size_gb              = number
    data_storage_size_tb        = number
    db_node_storage_size_gb     = number
    node_count                  = optional(number)
    ocpu_count                  = optional(number)
    disk_redundancy             = optional(string)


    ssh_public_keys = list(string)

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
    # Tags
    labels = optional(map(string), {})
  })
}