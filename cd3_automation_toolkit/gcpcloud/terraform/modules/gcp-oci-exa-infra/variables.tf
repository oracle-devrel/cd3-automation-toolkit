# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##########################################
## Variables Block - Oracle ExaInfra @GCP
## Create Oracle ExaInfra @GCP
##########################################

variable "labels" {
  description = "A mapping of tags which should be assigned to the Cloud Exadata Infrastructure."
  type        = map(string)
  default     = null
}

variable "infra_config" {
  description = "Exadata Infrastructure configuration object"
  type = object({
    # General
    location        = string
    gcp_oracle_zone = string
    project         = string

    # Infrastructure Details
    cloud_exadata_infrastructure_id = string
    display_name                    = string
    shape                           = string
    compute_count                   = number
    storage_count                   = number

    # Customer Contacts
    email = optional(string)

    # Maintenance Window
    maintenance_window = object({

      custom_action_timeout_mins       = optional(number, 15)
      days_of_week                     = optional(list(string), null)
      hours_of_day                     = optional(list(number), null)
      is_custom_action_timeout_enabled = optional(bool, false)
      lead_time_week                   = optional(number, null)
      months                           = optional(list(string), null)
      patching_mode                    = optional(string, "ROLLING")
      preference                       = optional(string, "NO_PREFERENCE")
      weeks_of_month                   = optional(list(number), null)
    })
    total_storage_size_gb = optional(string)

    # Tags
    labels = optional(map(string), {})
  })
}
