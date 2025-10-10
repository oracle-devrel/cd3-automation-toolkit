# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Security
## Create Cloud Guard Config
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "reporting_region" {
  description = "The reporting region value"
  type        = string
  default     = null
}

variable "self_manage_resources" {
  description = "Identifies if Oracle managed resources will be created by customers. If no value is specified false is the default."
  type        = bool
  default     = null
}

variable "status" {
  description = "Status of Cloud Guard Tenant. Allowed Values are DISABLED, ENABLED"
  type        = string
  default     = "ENABLED"
}

variable "tenancy_ocid" {
  description = "OCID of the tenancy"
  type        = string
  default     = null
}