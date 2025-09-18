# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Database
# Create MySQL DB Systems
############################

resource "oci_mysql_mysql_db_system" "db_system" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  shape_name          = var.shape_name
  subnet_id           = var.subnet_id

  admin_password = var.admin_password
  admin_username = var.admin_username

  backup_policy {
     is_enabled = var.backup_policy_is_enabled
     pitr_policy {
      is_enabled = var.pitr_policy_is_enabled
    }
    retention_in_days = var.backup_policy_retention_in_days
    window_start_time = var.backup_policy_window_start_time
  }

  configuration_id       = var.configuration_id
  crash_recovery         = var.crash_recovery
  data_storage_size_in_gb = var.data_storage_size_in_gb
  database_management    = var.database_management

  defined_tags = var.defined_tags

  deletion_policy {
    automatic_backup_retention = var.deletion_policy_automatic_backup_retention
    final_backup               = var.deletion_policy_final_backup
    is_delete_protected        = var.deletion_policy_is_delete_protected
  }

  description   = var.description
  display_name  = var.display_name
  fault_domain  = var.fault_domain
  freeform_tags = var.freeform_tags
  hostname_label = var.hostname_label
  ip_address     = var.ip_address
  is_highly_available = var.is_highly_available

  maintenance {
    window_start_time = var.maintenance_window_start_time
  }

  port   = var.port
  port_x = var.port_x
/*
  source {
    source_type = var.source_type
    backup_id   = var.backup_id
  }

 */
}



