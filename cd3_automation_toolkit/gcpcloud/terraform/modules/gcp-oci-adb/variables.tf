variable "labels" {
  description = "A mapping of tags which should be assigned to the Cloud Exadata Infrastructure."
  type        = map(string)
  default     = null
}

variable "adb_config" {
  description = "ADB configuration object"
  type = object({
    location                        = string
    project                         = string
    autonomous_database_id          = string
    database                        = string
    display_name                    = string
    admin_password                  = string

    create_odb_network          = bool
    create_odb_network_subnets  = bool
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
    n_character_set                 = string
    character_set                   = string
    license_type                    = string

    private_endpoint_ip             = optional(string)
    private_endpoint_label          = optional(string)

    is_auto_scaling_enabled         = optional(bool, false)
    is_storage_auto_scaling_enabled = optional(bool, false)

    maintenance_schedule_type       = optional(string)
    mtls_connection_required        = optional(string)
    backup_retention_period_days    = optional(number)
    email                           = optional(string)
  })

}

variable "odb_network_id" {
  description = "ODB Network ID"
  type        = string
  default     = null
}

variable "odb_client_subnet_id" {
  description = "ODB Client Subnet ID"
  type        = string
  default     = null
}
