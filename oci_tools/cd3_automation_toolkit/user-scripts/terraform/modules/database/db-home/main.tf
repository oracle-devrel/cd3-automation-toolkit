// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Database
# Create Database Db Home
############################

resource "oci_database_db_home" "new_database_db_home" {
  database {
    admin_password = var.admin_password

    #Optional
    backup_id                  = var.backup_id
    backup_tde_password        = var.backup_tde_password
    character_set              = var.character_set
    database_id                = var.database_id
    database_software_image_id = var.custom_database_image_name != null ? element([ for v in data.oci_database_database_software_images.custom_database_software_images[0].database_software_images : v.id if v.display_name == var.custom_database_image_name],0) : null
    db_backup_config {
            #Optional
            auto_backup_enabled = var.auto_backup_enabled
            auto_backup_window  = var.auto_backup_window
#            backup_destination_details {
#              id   = var.backup_dest_id
#              type = var.backup_dest_type
#            }
            recovery_window_in_days = var.recovery_window_in_days
    }
    db_name        = var.db_name
    db_workload    = var.db_workload
    defined_tags   = var.defined_tags
    freeform_tags  = var.freeform_tags
    ncharacter_set = var.ncharacter_set
    pdb_name       = var.pdbname
    #sid_prefix                           = var.sid_prefix
    tde_wallet_password                   = var.tde_wallet_password
    time_stamp_for_point_in_time_recovery = var.timestamp_for_point_in_time_recovery
  }
  #Optional
  database_software_image_id = var.custom_database_image_name != null ? element([ for v in data.oci_database_database_software_images.custom_database_software_images[0].database_software_images : v.id if v.display_name == var.custom_database_image_name], 0) : null
  db_system_id               = var.db_system_id
  db_version                 = var.db_version
  defined_tags               = var.defined_tags
  display_name               = var.display_name
  freeform_tags              = var.freeform_tags
  is_desupported_version     = var.is_desupported_version
  kms_key_id                 = var.kms_key_id
  kms_key_version_id         = var.kms_key_version_id
  source                     = var.db_source
  vm_cluster_id              = var.vm_cluster_id != null ? data.oci_database_cloud_vm_clusters.existing_cloud_vm_cluster[0].cloud_vm_clusters[0].id : null

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], database[0]["defined_tags"], database[0]["admin_password"]]
  }
}