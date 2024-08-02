# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Governance
# Create Tag Defaults
############################

variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy"
  default     = null
}
variable "quota_description" {
  type        = string
  description = "Quota description"
  default     = null
}
variable "quota_name" {
  type        = string
  description = "Quota name"
  default     = null
}
variable "quota_locks_type" {
  type        = string
  description = "Quota locks type"
  default     = null
}

variable "quota_locks_message" {
  type        = string
  description = "Quota lock message"
  default     = null
}

variable "quota_statements" {
  type        = list(string)
  description = "Quota statements"
  default     = []
}

variable "freeform_tags" {
  description = "Free-form tags for the quota"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the quota"
  type        = map(string)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

