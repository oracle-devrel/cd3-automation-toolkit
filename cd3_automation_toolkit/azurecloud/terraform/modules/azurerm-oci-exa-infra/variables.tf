# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Variables Block - Oracle ExaInfra @Azure
## Create Oracle ExaInfra @Azure
#####################################

# Mandatory
variable "location" {
  description = "The name of Azure Region where the Exadata Infrastructure should be. e.g. useast"
  type        = string
}

variable "name" {
  description = "The name of the Exadata Infrastructure at Azure"
  type        = string
  default     = "odaaz-infra"
}

variable "resource_group_name" {
  description = "The name of Resource Group in Azure"
  type        = string
  default     = "rg-oradb"
}

variable "zone" {
  description = "The availablty zone of the Exadata Infrastructure in Azure"
  type        = string
}

variable "compute_count" {
  description = "The number of compute servers for the Exadata infrastructure."
  type        = number
  default     = 2
}

variable "storage_count" {
  description = "The number of storage servers for the Exadata infrastructure."
  type        = number
  default     = 3
}

variable "shape" {
  description = "The shape of the Exadata infrastructure resource. e.g. Exadata.X9M"
  type        = string
  default     = "Exadata.X9M"
}
/*
variable "database_server_type" {
  description = "Database Server Type"
  type        = string
  default     = "X11M"
}

variable "storage_server_type" {
  description = "Storage Server Type"
  type        = string
  default     = "X11M-HC"
}
*/

# Optional
variable "customer_contacts" {
    description = "The email address used by Oracle to send notifications regarding databases and infrastructure. Provide up to 10 unique maintenance contact email addresses."
    type = list(string)
    default = []
}

variable "maintenance_window" {
  description = "maintenanceWindow properties"
  type = object({
      patching_mode = string
      preference = string
      lead_time_in_weeks = optional(number)
      months = optional(list(number))
      weeks_of_month = optional(list(number))
      days_of_week =optional(list(number))
      hours_of_day = optional(list(number))
  })
  default = {
    patching_mode = "Rolling"
    preference = "NoPreference"
  }
}

variable "tags" {
  description = "Resource tags for the Cloud Exadata Infrastructure"
  type        = map(string)
  default     = null
}