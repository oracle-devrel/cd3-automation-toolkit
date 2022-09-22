// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#################################
## Variables Block - Autonomous database
## Create autonomous database
#################################

variable "admin_password" {
  description = "Password for the admins"
  type        = string
}

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "cpu_core_count" {
  description = "The number of OCPU cores to be made available to the database"
  type        = number
}

variable "db_name" {
  description = "Name of the database"
  type        = string
}

variable "freeform_tags" {
  description = "Free-form tags for the DB"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the DB"
  type        = map(string)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "display_name" {
  description = "User-friendly name to the autonomous database"
  type        = string
}

variable "data_storage_size_in_tbs" {
  description = "Data storage size for the DB"
  type        = number
}

variable "db_version" {
  description = "the version of DB"
  type        = string
  default     = "19c"
}


variable "db_workload" {
  description = "The type of autonomous database-ATP or ADW"
  type        = string
  default     = ""
}