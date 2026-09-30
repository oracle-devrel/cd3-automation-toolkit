# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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

variable "prefix" {
  description = "prefix for detector and responder recipes display names"
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

variable "detector_recipe_rule_overrides" {
  description = "Detector-rule overrides keyed by Oracle detector recipe display name, then rule ID. An empty map preserves the cloned Oracle recipe rules."
  type = map(map(object({
    detector_rule_id = string
    is_enabled       = bool
    risk_level       = string
    labels           = optional(list(string), [])
  })))
  default = {}
}

variable "responder_recipe_rule_overrides" {
  description = "Responder-rule overrides keyed by Oracle responder recipe display name, then rule ID. An empty map preserves the cloned Oracle recipe rules."
  type = map(map(object({
    responder_rule_id = string
    is_enabled        = bool
  })))
  default = {}
}
