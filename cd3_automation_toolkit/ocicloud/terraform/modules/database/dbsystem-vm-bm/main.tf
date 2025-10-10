# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Database
# Create Database VM BM
############################

resource "oci_database_db_system" "database_db_system" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  hostname            = var.hostname
  shape               = var.shape
  ssh_public_keys     = var.ssh_public_keys
  subnet_id           = var.subnet_id
  disk_redundancy     = var.disk_redundancy

  #Optional
  node_count = var.node_count
  nsg_ids    = var.nsg_ids != null ? (local.nsg_ids == null ? ["INVALID NSG Name"] : local.nsg_ids) : null
  #private_ip       = var.private_ip
  #sparse_diskgroup = var.sparse_diskgroup
  time_zone = var.time_zone

  db_home {
    database {
      admin_password = var.admin_password
      character_set  = var.character_set #(Applicable when source=NONE)
      db_backup_config {
        #(Applicable when source=DB_SYSTEM | NONE)
        #Optional
        auto_backup_enabled = var.auto_backup_enabled
        #        backup_destination_details {
        #          #Optional
        #          id = var.backup_destination_id
        #          type = var.backup_destination_type
        #        }
        recovery_window_in_days = var.recovery_window_in_days
      }
      db_name        = var.db_name
      db_workload    = var.db_workload
      ncharacter_set = var.ncharacter_set #(Applicable when source=NONE)
      pdb_name       = var.pdb_name       #(Applicable when source=NONE)
      #sid_prefix = var.sid_prefix
      #tde_wallet_password = var.tde_wallet_password
      defined_tags  = var.defined_tags
      freeform_tags = var.freeform_tags
    }
    #Optional
    # database_software_image_id = var.db_software_image_id      #(Applicable when source=DB_BACKUP | NONE)
    db_version   = var.db_version
    display_name = var.db_home_display_name

  }

  cluster_name            = var.cluster_name
  cpu_core_count          = var.cpu_core_count
  data_storage_percentage = var.data_storage_percentage
  data_storage_size_in_gb = var.data_storage_size_in_gb
  database_edition        = var.database_edition
  #  db_system_options {         #Optional
  #    #Optional
  #    storage_management = var.db_storage_management
  #  }
  license_model = var.license_model
  display_name  = var.display_name

  #fault_domains = []
  #kms_key_id = ""
  #kms_key_version_id = ""

  #  maintenance_window_details {                  #(Applicable when source=NONE)
  #Optional
  #    custom_action_timeout_in_mins = ""
  #    days_of_week {
  #      #Optional
  #      name = ""
  #    }
  #    hours_of_day = []
  #    is_custom_action_timeout_enabled = false
  #    lead_time_in_weeks = ""
  #    months {
  #      #Optional
  #      name = ""
  #    }
  #   patching_mode = ""                # (Applicable when source=NONE)
  #   preference = ""                   # (Applicable when source=NONE)
  #    weeks_of_month = []               # (Applicable when source=NONE)
  #}
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [db_home[0].database[0].defined_tags["Oracle-Tags.CreatedOn"],db_home[0].database[0].defined_tags["Oracle-Tags.CreatedBy"],db_home[0].database[0].db_backup_config[0].auto_full_backup_day]
  }

}



