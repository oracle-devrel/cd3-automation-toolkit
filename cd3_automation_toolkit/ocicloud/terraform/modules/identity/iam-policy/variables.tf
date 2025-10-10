# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Identity
# Create Policies
############################

variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy."
  default     = null
}

variable "policy_name" {
  type        = string
  description = "The name you assign to the policy during creation.  "
  default     = null
}

variable "policy_description" {
  type        = string
  description = "The description you assign to the policy. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "policy_statements" {
  type        = list(string)
  description = "Define policy consists of one or more policy statements. "
  default     = null
}

variable "policy_compartment_id" {
  type        = string
  description = "The compartment id where policy is created."
  default     = null
}

variable "policy_version_date" {
  type        = string
  description = "The date of the policy version."
  default     = null
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