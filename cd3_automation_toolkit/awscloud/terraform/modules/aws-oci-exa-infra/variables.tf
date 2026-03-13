# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
## Variables Block - Oracle ExaInfra @Azure
## Create Oracle ExaInfra @Azure
############################################

variable "infra_key" {
  description = "Infrastructure key/name from the map"
  type        = string
}

variable "tags" {
  description = "A mapping of tags which should be assigned to the Cloud Exadata Infrastructure."
  type        = map(string)
  default     = null
}

variable "infra_config" {
  description = "Exadata Infrastructure configuration object"
  type = object({
    # General
    environment          = string
    region               = string
    availability_zone    = string
    availability_zone_id = string

    # Infrastructure Details
    display_name         = string
    shape                = string
    compute_count        = number
    storage_count        = number
    database_server_type = string
    storage_server_type  = string

    # Customer Contacts
    customer_contacts = list(object({ email = string }))

    # Maintenance Window
    maintenance_window = object({
      patching_mode                    = optional(string, "ROLLING")
      preference                       = optional(string, "NO_PREFERENCE")
      is_custom_action_timeout_enabled = optional(bool, false)
      custom_action_timeout_in_mins    = optional(number, 15)
      days_of_week                     = optional(list(string), null)
      hours_of_day                     = optional(list(number), null)
      lead_time_in_weeks               = optional(number, null)
      months                           = optional(list(string), null)
      weeks_of_month                   = optional(list(number), null)
    })

    # Tags
    tags = optional(map(string), {})
  })
}}