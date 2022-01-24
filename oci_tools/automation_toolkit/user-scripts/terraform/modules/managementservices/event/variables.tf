// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - ManagementServices
# Create Events
############################


variable "compartment_name" {
  type = string
  description = "The compartment ID where alarm is created."
  default = null
}

variable "event_name" {
  type = string
  description = "The name you assign to the event rule during creation."
  default = null
}

variable "destinations" {
  type = list
  default = null
}

variable "is_enabled" {
  type = bool
  description = "The alarm is enabled or disabled."
  default     = null
}

variable "metric_compartment_name" {
  type = string
  description = "The compartment ID for the metric"
  default     = null
}

variable "namespace" {
  type = string
  default     = null
}

variable "query" {
  type = string
  default     = null
}

variable "severity" {
  type = string
  description = "Severity of the Alarm"
  default     = null
}

variable "body" {
  type = string
  default     = null
}

variable "message_format" {
  type = string
  default     = null
}

variable "trigger_delay_minutes" {
  type = string
  default     = null
}

variable "repeat_notification_duration" {
  type = string
  default     = null
}

variable "defined_tags" {
type = map
default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
            "Oracle-Tags.CreatedBy"= "$${iam.principal.name}"
          }
}

variable "freeform_tags" {
  type = map
  default = {}
}