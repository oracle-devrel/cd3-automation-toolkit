// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
# Variables Block - Database PDB
# Create Databases
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