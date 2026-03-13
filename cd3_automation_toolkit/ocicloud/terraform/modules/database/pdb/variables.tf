# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

################################
# Variables Block - Database PDB
# Create PDBs
################################

variable "container_database_id" {
  type = string
  default = null
}
variable "pdb_admin_password" {
  type = string
  default = null
}
variable "pdb_name" {
  type = string
  default = null
}
variable "tde_wallet_password" {
  type = string
  default = null
}
variable "defined_tags" {
  type = map(string)
  default = null
}
variable "freeform_tags" {
  type = map(string)
  default = null
}

variable "exadata_infrastructure_comp_id" {
  description = ""
  type        = string
  default     = null
}

