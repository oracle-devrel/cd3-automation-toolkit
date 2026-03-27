# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

############################
# Variables Block - DB Home
# Create Database DB Home
############################

#Required
variable "compartment_id" {
  type    = string
  default = null
}

variable "defined_tags" {
  description = ""
  type        = map(any)
  default     = {}
}

variable "freeform_tags" {
  description = ""
  type        = map(any)
  default     = null
}

variable "display_name" {
  description = ""
  type        = string
  default     = null
}
variable "db_source" {
  description = ""
  type        = string
  default     = null
}

variable "db_version" {
  description = ""
  type        = string
  default     = null
}

variable "vm_cluster_id" {
  description = ""
  type        = string
  default     = null
}

variable "exadata_infrastructure_id" {
  description = ""
  type        = string
  default     = null
}

variable "exadata_infrastructure_comp_id" {
  description = ""
  type        = string
  default     = null
}



