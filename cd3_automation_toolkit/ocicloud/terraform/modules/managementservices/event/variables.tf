# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - ManagementServices
# Create Events
############################


variable "compartment_id" {
  type        = string
  description = "The compartment ID where alarm is created."
  default     = null
}

variable "event_name" {
  type        = string
  description = "The name you assign to the event rule during creation."
  default     = null
}

variable "condition" {
  type    = string
  default = ""
}

variable "topic_name" {}

variable "key_name" {
  type    = string
  default = ""
}

variable "description" {
  type    = string
  default = null
}

variable "actions" {
  type    = map(any)
  default = {}
}
variable "destinations" {
  type    = list(any)
  default = null
}

variable "is_enabled" {
  type        = bool
  description = "The alarm is enabled or disabled."
  default     = null
}

variable "metric_compartment_name" {
  type        = string
  description = "The compartment ID for the metric"
  default     = null
}

variable "namespace" {
  type    = string
  default = null
}

variable "query" {
  type    = string
  default = null
}

variable "severity" {
  type        = string
  description = "Severity of the Alarm"
  default     = null
}

variable "body" {
  type    = string
  default = null
}

variable "message_format" {
  type    = string
  default = null
}

variable "trigger_delay_minutes" {
  type    = string
  default = null
}

variable "repeat_notification_duration" {
  type    = string
  default = null
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}