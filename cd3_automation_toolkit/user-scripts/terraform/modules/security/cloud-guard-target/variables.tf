// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#################################
## Variables Block - Security
## Create Cloud Guard Target
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "display_name" {
  description = "DetectorTemplate identifier."
  type        = string
  default     = null
}

variable "target_resource_id" {
  description = "Resource ID which the target uses to monitor."
  type        = string
  default     = null
}

variable "target_resource_type" {
  description = "possible type of targets(compartment/HCMCloud/ERPCloud)"
  type        = string
  default     = null
}

variable "state" {
  description = "The current state of the DetectorRule. Allowed Values: ACTIVE, CREATING, DELETED, DELETING, FAILED, INACTIVE, UPDATING"
  type        = string
  default     = null
}

variable "description" {
  description = "The target description."
  type        = string
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

variable "tenancy_ocid" {}

variable "target_responder_recipes" {}

variable "target_detector_recipes" {}

