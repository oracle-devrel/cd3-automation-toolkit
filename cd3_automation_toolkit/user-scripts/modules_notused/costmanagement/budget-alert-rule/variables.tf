# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Cost Management
## Create Budget Alert Rule
#################################

variable "budget_id" {
  description = "The unique budget OCID."
  type        = string
}

variable "threshold" {
  description = "The threshold for triggering the alert, expressed as a whole number or decimal value. If the thresholdType is ABSOLUTE, the threshold can have at most 12 digits before the decimal point, and up to two digits after the decimal point. If the thresholdType is PERCENTAGE, the maximum value is 10000 and can have up to two digits after the decimal point."
  type        = string
}

variable "threshold_type" {
  description = "The type of threshold."
  type        = string
}

variable "type" {
  description = " The type of the alert. Valid values are ACTUAL (the alert triggers based on actual usage), or FORECAST (the alert triggers based on predicted usage)."
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

variable "description" {
  description = "The description of the budget."
  type        = string
}

variable "display_name" {
  description = "The displayName of the budget. Avoid entering confidential information."
  type        = string
}

variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type        = map(string)
}

variable "message" {
  description = "The message to be sent to the recipients when the alert rule is triggered."
  type        = string
}

variable "recipients" {
  description = "The audience that receives the alert when it triggers. An empty string is interpreted as null."
  type        = string
}
