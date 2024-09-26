# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Database
# Create ExaInfra
############################

variable "availability_domain" {
  type    = string
  default = null
}
variable "compartment_id" {
  type    = string
  default = ""
}
variable "display_name" {
  type    = string
  default = ""
}
variable "shape" {
  type    = string
  default = ""
}
variable "compute_count" {
  type = number
}
variable "customer_contacts_email" {
  type    = string
  default = ""
}
variable "defined_tags" {
  type    = map(any)
  default = {}
}
variable "freeform_tags" {
  type    = map(any)
  default = {}
}
variable "maintenance_window_preference" {
  type    = string
  default = ""
}
variable "maintenance_window_days_of_week_name" {
  type    = string
  default = ""
}
variable "maintenance_window_hours_of_day" {
  type    = list(number)
  default = []
}
variable "maintenance_window_lead_time_in_weeks" {
  type    = number
  default = 0
}
variable "maintenance_window_months_name" {
  type    = string
  default = ""
}
variable "maintenance_window_weeks_of_month" {
  type    = list(number)
  default = []
}
variable "storage_count" {
  type = number
}
