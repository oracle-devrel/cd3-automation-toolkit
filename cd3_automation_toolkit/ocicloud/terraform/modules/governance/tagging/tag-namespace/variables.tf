# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Governance
# Create Namespaces
############################

variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy."
  default     = null
}

variable "compartment_id" {
  type        = string
  description = "The OCID of the parent compartment containing the compartment. Allow for sub-compartments creation"
  default     = null
}

variable "description" {
  type        = string
  description = "The description you assign to the namespace. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "name" {
  type        = string
  description = "Namespace name"
  default     = null
}

variable "is_retired" {
  type        = bool
  description = "Enable to retire the namespace."
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

