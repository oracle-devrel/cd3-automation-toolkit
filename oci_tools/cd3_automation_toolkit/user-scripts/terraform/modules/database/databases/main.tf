// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

###########################
# Resource Block - Database
# Create Databases
###########################

resource "oci_database_database" "new_database" {
  count = length(var.databases)
  #Required
  dynamic "database" {
    for_each = var.databases
    content {
      #Required
      admin_password = database.value["admin_password"]
      db_name        = database.value["db_name"]

      #Optional
      backup_id                  = database.value["backup_id"]
      backup_tde_password        = database.value["backup_tde_password"]
      character_set              = database.value["character_set"]
      database_software_image_id = var.custom_database_image_name != null ? data.oci_database_database_software_images.custom_database_software_images.database_software_images[0].id : null
      db_backup_config {
        #Optional
        auto_backup_enabled = database.value["auto_backup_enabled"]
        auto_backup_window  = database.value["auto_backup_window"]
        backup_destination_details {

          #Optional
          id   = database.value["backup_dest_id"]
          type = database.value["backup_dest_type"]
        }
        recovery_window_in_days = database.value["recovery_window_in_days"]
      }
      db_unique_name      = database.value["db_unique_name"]
      db_workload         = database.value["db_workload"]
      defined_tags        = database.value["defined_tags"]
      freeform_tags       = database.value["freeform_tags"]
      ncharacter_set      = database.value["ncharacter_set"]
      pdb_name            = database.value["pdb_name"]
      sid_prefix          = database.value["sid_prefix"]
      tde_wallet_password = database.value["tde_wallet_password"]
    }
  }
  db_home_id = data.oci_database_db_homes.existing_db_home.db_homes[0].id
  source     = var.db_source

  #Optional
  db_version         = var.db_version
  kms_key_id         = var.kms_key_id
  kms_key_version_id = var.kms_key_version_id
}