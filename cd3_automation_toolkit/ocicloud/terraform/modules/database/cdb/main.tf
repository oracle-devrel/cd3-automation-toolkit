# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
###############################
# Resource Block - Database CDB
# Create Databases
###############################

resource "oci_database_database" "database_database" {
  #Required
  dynamic "database" {
    for_each = var.database
    content {
      admin_password = database.value.admin_secret_id != null ? base64decode(data.oci_secrets_secretbundle.admin_secrets[database.value.db_name].secret_bundle_content[0].content) : database.value.admin_password
      db_name        = database.value["db_name"]
      character_set  = database.value["character_set"]
      db_backup_config {
        auto_backup_enabled       = database.value["auto_backup_enabled"]
        auto_backup_window        = database.value["auto_backup_window"]
        auto_full_backup_day      = database.value["auto_full_backup_day"]
        auto_full_backup_window   = database.value["auto_full_backup_window"]
        run_immediate_full_backup = database.value["run_immediate_full_backup"]
        backup_deletion_policy    = database.value["backup_deletion_policy"]
        /*
        backup_destination_details {
          id             = database.value["backup_dest_id"]
          type           = database.value["backup_dest_type"]
          dbrs_policy_id = database.value["dbrs_policy_id"] != null ? (length(regexall("ocid1.recoveryservicepolicy.*", database.value["dbrs_policy_id"])) > 0 ? database.value["dbrs_policy_id"] : data.oci_recovery_protection_policies.protection_policies[database.value.db_name].protection_policy_collection[0].items[0].id) : null
        }
        */
          dynamic "backup_destination_details" {
    for_each = database.value["auto_backup_enabled"] ? [1] : []
    content {
      id   = database.value["backup_dest_id"]
      type = database.value["backup_dest_type"]
      dbrs_policy_id = database.value["dbrs_policy_id"] != null ? (length(regexall("ocid1.recoveryservicepolicy.*", database.value["dbrs_policy_id"])) > 0 ? database.value["dbrs_policy_id"] : data.oci_recovery_protection_policies.protection_policies[database.value.db_name].protection_policy_collection[0].items[0].id) : null
    }
          }
        recovery_window_in_days = database.value["recovery_window_in_days"]
      }
      db_unique_name      = database.value["db_unique_name"]
      defined_tags        = database.value["defined_tags"]
      freeform_tags       = database.value["freeform_tags"]
      ncharacter_set      = database.value["ncharacter_set"]
      pdb_name            = database.value["pdb_name"]
      sid_prefix          = database.value["sid_prefix"]
      tde_wallet_password = database.value.tde_wallet_secret_id != null ? base64decode(data.oci_secrets_secretbundle.tde_wallet_secrets[database.value.db_name].secret_bundle_content[0].content) : database.value.tde_wallet_password
    }
  }
  db_home_id = var.db_home_id
  source     = var.db_source
  #db_version = var.db_version


  lifecycle {
    ignore_changes= [source,database[0].defined_tags["Oracle-Tags.CreatedOn"],database[0].defined_tags["Oracle-Tags.CreatedBy"],database[0].db_backup_config[0].backup_destination_details[0].vpc_user]
  }

}

/*
resource "time_sleep" "wait_5_minutes" {
  depends_on = [oci_database_database.database_database]
  create_duration = "300s"

}
  */