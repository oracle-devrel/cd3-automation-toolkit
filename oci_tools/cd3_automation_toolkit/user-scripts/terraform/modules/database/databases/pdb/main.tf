// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

###############################
# Resource Block - Database PDB
# Create Databases
###############################

resource "oci_database_pluggable_database" "new_pluggable_database" {
  container_database_id = var.container_database_id
  pdb_admin_password    = var.pdb_admin_password
  pdb_name              = var.pdb_name
  tde_wallet_password   = var.tde_wallet_password
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["SE_Details.SE_Name"]]
  }
}

resource "time_sleep" "wait_5_minutes" {
  depends_on = [oci_database_pluggable_database.new_pluggable_database]

  create_duration = "300s"
}
