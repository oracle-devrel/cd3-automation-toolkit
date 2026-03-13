# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
###############################
# Data Block - Database CDB
# Create Databases
###############################

locals {
  admin_secret_map = {
    for database in var.database :
    database.db_name => database.admin_secret_id
    if database.admin_secret_id != null
  }

  tde_wallet_secret_map = {
    for database in var.database :
    database.db_name => database.tde_wallet_secret_id
    if database.tde_wallet_secret_id != null
  }

  dbrs_policy_map = {
    for database in var.database :
    database.db_name => database.dbrs_policy_id
    if database.dbrs_policy_id != null
  }
}

data "oci_recovery_protection_policies" "protection_policies" {
  for_each       = local.dbrs_policy_map
  compartment_id = var.compartment_id
  display_name   = each.value
}

data "oci_secrets_secretbundle" "admin_secrets" {
  for_each  = local.admin_secret_map
  secret_id = each.value
}

data "oci_secrets_secretbundle" "tde_wallet_secrets" {
  for_each  = local.tde_wallet_secret_map
  secret_id = each.value
}

/*
data "oci_database_cloud_vm_clusters" "existing_cloud_vm_clusters" {
  count = var.vm_cluster_name != null ? 1 : 0
  compartment_id = var.compartment_id
  display_name   = var.vm_cluster_name
  state = "Available"
}
*/





