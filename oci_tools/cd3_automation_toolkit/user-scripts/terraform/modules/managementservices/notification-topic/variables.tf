// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - ManagementServices
# Create Notifications_Topics
############################

variable "compartment_id" {
  type = string
}

variable "topic_name" {
  type = string
}
variable "description" {
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