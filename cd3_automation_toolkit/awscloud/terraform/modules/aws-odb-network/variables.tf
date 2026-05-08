# ========================================
# Module: aws-odb-network / variables.tf
# ========================================

variable "network_key" {
  description = "Network map key (same as display_name)"
  type        = string
}

variable "network_config" {
  description = "ODB Network configuration including optional embedded peering"
  type = object({
    # Required
    display_name         = string
    availability_zone_id = string
    client_subnet_cidr   = string
    s3_access            = string          # "ENABLED" | "DISABLED"
    zero_etl_access      = string          # "ENABLED" | "DISABLED"

    # Optional network fields
    backup_subnet_cidr = optional(string, null)
    availability_zone  = optional(string, null)

    # Mutually exclusive — set only one or neither
    custom_domain_name = optional(string, null)
    default_dns_prefix = optional(string, null)

    tags = optional(map(string), {})

    # Embedded peering config
    create_odb_peering   = optional(bool, false)
    peering_display_name = optional(string, null) # Required when create_odb_peering = true
    peer_vpc_id          = optional(string, null) # Required when create_odb_peering = true
    peering_region       = optional(string, null)
    peering_tags         = optional(map(string), {})
  })
}
