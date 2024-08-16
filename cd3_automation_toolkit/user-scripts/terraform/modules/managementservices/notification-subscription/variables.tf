# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - ManagementServices
# Create Notifications_Subscriptions
############################

variable "compartment_id" {
  type = string
}

variable "endpoint" {
  type = string
}

variable "protocol" {
  type = string
}

variable "topic_id" {
  type = string
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