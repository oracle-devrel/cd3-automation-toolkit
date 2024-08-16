# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
# Variables Block - Service Connector
# Create Service Connector Hub
#####################################

variable "compartment_id" {
  type    = string
  default = null
}
variable "logs_compartment_id" {
  type    = string
  default = null
}
variable "log_group_names" {
  type    = list(any)
  default = []
}
variable "destination_log_group_id" {
  type    = map(any)
  default = {}
}
variable "target_log_source_identifier" {
  type    = string
  default = null
}
variable "source_monitoring_details" {
  type    = map(any)
  default = {}
}
variable "target_monitoring_details" {
  type    = map(any)
  default = {}
}
variable "function_details" {
  type    = list(string)
  default = null
}
variable "display_name" {
  type    = string
  default = null
}
variable "description" {
  type    = string
  default = null
}
variable "stream_id" {
  type    = map(any)
  default = {}
}
variable "source_stream_id" {
  type    = map(any)
  default = {}
}
variable "source_kind" {
  type    = string
  default = null
}
variable "target_kind" {
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

###############
#Object Storage
###############
variable "bucket_name" {
  type    = string
  default = null
}
variable "object_name_prefix" {
  type    = string
  default = null
}
###############
#Notifications
###############
variable "topic_id" {
  type    = map(any)
  default = {}
}
variable "enable_formatted_messaging" {
  type    = bool
  default = false
}
variable "source_details" {
  type    = map(any)
  default = {}
}
variable "target_details" {
  type    = map(any)
  default = {}
}