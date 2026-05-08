# ========================================
# Module: aws-oci-exa-vmcluster / variables.tf
# ========================================

variable "cluster_key" {
  description = "Cluster map key"
  type        = string
}

variable "tags" {
  description = "Tags for the VM Cluster"
  type        = map(string)
  default     = null
}

variable "create_odb_network" {
  description = "true = use created_odb_network_id | false = look up existing network by display_name"
  type        = bool
}

variable "created_odb_network_id" {
  description = "ID of the newly created ODB network. Passed from root when create_odb_network = true. Null when create_odb_network = false."
  type        = string
  default     = null
}

variable "cluster_config" {
  type = object({
    # Network control
    create_odb_network = bool   # true = create new | false = use existing
    odb_network_name   = string # Always the network display_name

    # Mandatory
    region                      = string
    exadata_infrastructure_name = string
    display_name                = string
    cluster_name                = string
    gi_version                  = string
    hostname_prefix             = string
    cpu_core_count              = number
    memory_size_in_gbs          = number
    data_storage_size_in_tbs    = number
    db_node_storage_size_in_gbs = number
    ssh_public_keys             = list(string)

    # Optional
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

    # Immutable
    is_local_backup_enabled     = bool
    is_sparse_diskgroup_enabled = bool

    tags = optional(map(string), {})
  })
}
