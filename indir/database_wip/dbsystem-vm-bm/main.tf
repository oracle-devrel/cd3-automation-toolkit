// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Database
# Create DBSystems-VM-BM
############################

resource "oci_database_db_system" "db_system" {
  count = var.db_system_display_name != null ? 1 : 0
  #Required
  compartment_id      = var.compartment_name
  display_name        = var.db_system_display_name
  availability_domain = var.availability_domain
  cpu_core_count      = var.cpu_core_count
  database_edition    = var.database_edition
  db_home {
        database {
          admin_password = var.db_admin_password
          db_name = var.db_name
          character_set = var.character_set
          ncharacter_set = var.ncharacter_set
          db_workload = var.db_workload
          pdb_name = var.pdb_name
          db_backup_config {
            auto_backup_enabled = var.enable_automatic_backups
            recovery_window_in_days = var.back_up_retention_period
            }
          }
          db_version = var.db_version
        }
  disk_redundancy = var.disk_redundancy
  shape = var.shape
  subnet_id = var.subnet_name
  ssh_public_keys = var.ssh_public_keys
  hostname = var.hostname_prefix
  data_storage_size_in_gb = var.data_storage_size_in_gb
  data_storage_percentage = var.data_storage_percentage
  license_model = var.license_model
  node_count = var.node_count
  time_zone = var.time_zone

  #Optional
  defined_tags = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
    }

}



  is_enabled     = var.is_enabled
  description    = var.description
  condition      = var.condition
  actions        = var.actions

  #Optional
  defined_tags = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
    }
}
