// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#################################
## Variables Block - Public IP Pool
## Create Public IP Pool
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
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
