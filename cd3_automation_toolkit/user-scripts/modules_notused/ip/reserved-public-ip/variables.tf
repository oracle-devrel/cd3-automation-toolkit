# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Reserved IP
## Create Reserved IP
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "lifetime" {
  description = "Defines when the public IP is deleted and released back to the Oracle Cloud Infrastructure public IP pool"
  type        = string
  default     = null
}

variable "private_ip_id" {
  description = "The OCID of the private IP to assign the public IP to."
  type        = string
  default     = null
}

variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the volume"
  type        = map(string)
}

variable "display_name" {
  description = "User-friendly name to the volume"
  type        = string
}

variable "public_ip_pool_id" {
  description = "The OCID of the public IP pool."
  type        = string
  default     = null
}
