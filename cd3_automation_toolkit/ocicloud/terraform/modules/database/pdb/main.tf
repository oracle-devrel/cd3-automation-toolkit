# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

###############################
# Resource Block - Database PDB
# Create PDBs
###############################



resource "oci_database_pluggable_database" "pluggable_database" {
  container_database_id = var.container_database_id
  pdb_admin_password      =    var.pdb_admin_password
  pdb_name              = var.pdb_name
  tde_wallet_password   = var.tde_wallet_password  #TDE wallet password is not required when Database is configured to use customer-managed (Vault service) key
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags

  /*
  lifecycle {
    ignore_changes = [pdb_admin_password,pdb_name,tde_wallet_password,
      defined_tags["SE_Details.SE_Name"], defined_tags["Oracle-Tags.CreatedOn"],
      defined_tags["Oracle-Tags.CreatedBy"]]

  }
        */
}
/*
resource "time_sleep" "wait_5_minutes" {
  depends_on = [oci_database_pluggable_database.new_pluggable_database]

  create_duration = "300s"
}
*/