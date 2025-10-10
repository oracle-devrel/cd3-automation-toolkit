# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Cost Management
## Create Budget
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the Budget"
  type        = string
}

variable "amount" {
  description = "The amount of the budget expressed as a whole number in the currency of the customer's rate card."
  type        = number
}

variable "reset_period" {
  description = "The reset period for the budget. Valid value is MONTHLY."
  type        = string
}

variable "budget_processing_period_start_offset" {
  description = "The number of days offset from the first day of the month, at which the budget processing period starts."
  type        = string
  default     = null
}

variable "processing_period_type" {
  description = "The type of the budget processing period. Valid values are INVOICE and MONTH."
  type        = string
  default     = null
}

variable "defined_tags" {
  description = "Defined tags for the volume"
  type        = map(string)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type        = map(string)
}

variable "description" {
  description = "The description of the budget."
  type        = string
}

variable "display_name" {
  description = "The displayName of the budget. Avoid entering confidential information."
  type        = string
}

variable "budget_start_date" {
type = string
description = "The date when the one-time budget begins. For example, 2023-03-23. The date-time format conforms to RFC 3339, and will be truncated to the starting point of the date provided after being converted to UTC time."
}

variable "budget_end_date" {
type = string
description = "The date when the one-time budget concludes. For example, 2023-03-23. The date-time format conforms to RFC 3339, and will be truncated to the starting point of the date provided after being converted to UTC time."
}


variable "target_type" {
  description = "The type of target on which the budget is applied."
  type        = string
}

variable "targets" {
  description = "The list of targets on which the budget is applied. If targetType is 'COMPARTMENT', the targets contain the list of compartment OCIDs. If targetType is 'TAG', the targets contain the list of cost tracking tag identifiers in the form of '{tagNamespace}.{tagKey}.{tagValue}'. Curerntly, the array should contain exactly one item."
  type        = list(any)
}
