# ========================================
# Root - Input Variable Declarations
# ========================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_access_key" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
  default     = "<ACCESSKEY"
}

variable "aws_secret_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
  default     = "ACCESSSECRETKEY"
}

# ========================================
# ODB Networks
# Key = display_name of the network.
# Peering config is embedded inside each network entry via create_odb_peering.
# ========================================

variable "odb_networks_config" {
  description = "Map of ODB networks to create. Key = display_name. Peering config is embedded per network."
  type = map(object({
    # Required
    display_name         = string
    availability_zone_id = string # e.g. "usw2-az3"
    client_subnet_cidr   = string # e.g. "10.10.1.0/24"
    s3_access            = string # "ENABLED" | "DISABLED"
    zero_etl_access      = string # "ENABLED" | "DISABLED"

    # Optional network fields
    backup_subnet_cidr = optional(string, null) # Not required for Autonomous DB
    availability_zone  = optional(string, null) # e.g. "us-west-2c"

    # Mutually exclusive — set only one or neither
    custom_domain_name = optional(string, null)
    default_dns_prefix = optional(string, null)

    tags = optional(map(string), {})

    # Peering — embedded inside the network config
    # create_odb_peering = true  → creates a peering connection for this network
    # create_odb_peering = false → no peering created for this network
    create_odb_peering   = optional(bool, false)
    peering_display_name = optional(string, null) # Required when create_odb_peering = true
    peer_vpc_id          = optional(string, null) # Required when create_odb_peering = true
    peering_region       = optional(string, null) # Optional
    peering_tags         = optional(map(string), {})
  }))
  default = {}
}

# ========================================
# Exadata Infrastructure
# ========================================

variable "aws_oci_exa_infra" {
  description = "Map of Exadata Infrastructure configurations."
  type = map(object({
    region               = string
    availability_zone    = optional(string, null) # Optional — availability_zone_id is sufficient
    availability_zone_id = string
    display_name         = string
    shape                = string
    compute_count        = number
    storage_count        = number
    database_server_type = string
    storage_server_type  = string
    customer_contacts    = list(object({ email = string }))

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

    tags = optional(map(string), {})
  }))
}

# ========================================
# VM Clusters
#
# create_odb_network = true  → network is created by Terraform.
#                              odb_network_name must match the key (display_name)
#                              in odb_networks_config.
# create_odb_network = false → existing network is used.
#                              odb_network_name must match the display_name of
#                              the already existing ODB network.
#
# odb_network_name is always required and always holds the real network name.
# No null values needed in tfvars.
# ========================================

variable "aws_oci_exa_vmclusters" {
  description = "Map of VM Cluster configurations."
  type = map(object({
    # Network control — per cluster
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
  }))
}
