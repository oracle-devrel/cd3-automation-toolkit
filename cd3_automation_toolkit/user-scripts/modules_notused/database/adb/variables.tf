# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Autonomous database
## Create autonomous database
#################################

variable "admin_password" {
  description = "Password for the admins"
  type        = string
}

variable "character_set" {
  type = string
}

variable "customer_contacts" {
  description = "The customer_contacts of ADB"
  type        = list(string)

}

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "cpu_core_count" {
  description = "The number of OCPU cores to be made available to the database"
  type        = number
}

variable "database_edition" {
  description = "The database edition of ADB"
  type        = string
}

variable "data_storage_size_in_tbs" {
  description = "Data storage size for the DB"
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

variable "db_version" {
  description = "the version of DB"
  type        = string
}


variable "db_workload" {
  description = "The type of autonomous database-ATP or ADW"
  type        = string
}

variable "license_model" {
  description = "The license model for ADB"
  type        = string

}

variable "ncharacter_set" {
  description = "The ncharacter set of ADB"
  type        = string

}

variable "network_compartment_id" {
  description = "The network compartment of the subnet"
  type        = string
  default     = ""
}

variable "network_security_group_ids" {
  description = "NSGs to be attahced to ADB"
  type        = any
  default     = ""
}

variable "subnet_id" {
  description = "The subnet name into which the ADB will be launched"
  type        = string
  default     = ""
}

variable "vcn_name" {
  type    = string
  default = ""
}

variable "whitelisted_ips" {
  type    = list(string)
  default = []
}
