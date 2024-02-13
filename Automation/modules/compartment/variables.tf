// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Identity
# Create Compartments
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

variable "compartment_name" {
  type        = string
  description = "The name you assign to the compartment during creation. The name must be unique across all compartments in the tenancy. "
  default     = null
}

variable "compartment_description" {
  type        = string
  description = "The description you assign to the compartment. Does not have to be unique, and it's changeable. "
  default     = "Compartment for OCI Automation WorkVM and related components"
}

variable "enable_delete" {
  type        = bool
  description = "Enable compartment delete on destroy. If true, compartment will be deleted when `terraform destroy` is executed; If false, compartment will not be deleted on `terraform destroy` execution"
  default     = false
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
