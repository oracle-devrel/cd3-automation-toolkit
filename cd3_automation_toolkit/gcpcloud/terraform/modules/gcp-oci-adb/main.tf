resource "google_oracle_database_autonomous_database" "autonomous_database"{

  location                        = var.adb_config.location
  project                         = var.adb_config.project
  autonomous_database_id          = var.adb_config.autonomous_database_id
  database                        = var.adb_config.database
  display_name                    = var.adb_config.display_name
  admin_password                  = var.adb_config.admin_password
  odb_network            = var.odb_network_id
  odb_subnet             = var.odb_client_subnet_id
  properties {
    compute_count                   = var.adb_config.compute_count
    cpu_core_count                  = var.adb_config.cpu_core_count
    data_storage_size_tb            = var.adb_config.data_storage_size_tb
    data_storage_size_gb            = var.adb_config.data_storage_size_gb
    db_version                      = var.adb_config.db_version
    db_workload                     = var.adb_config.db_workload
    db_edition                      = var.adb_config.db_edition
    n_character_set                 = var.adb_config.n_character_set
    character_set                   = var.adb_config.character_set
    license_type                    = var.adb_config.license_type

    private_endpoint_ip             = var.adb_config.private_endpoint_ip
    private_endpoint_label          = var.adb_config.private_endpoint_label

    is_auto_scaling_enabled         = var.adb_config.is_auto_scaling_enabled
    is_storage_auto_scaling_enabled = var.adb_config.is_storage_auto_scaling_enabled

    maintenance_schedule_type       = var.adb_config.maintenance_schedule_type
    mtls_connection_required        = var.adb_config.mtls_connection_required
    backup_retention_period_days    = var.adb_config.backup_retention_period_days
    customer_contacts {
      email = var.adb_config.email
      }
  }
  deletion_protection = "true"
  lifecycle {
    ignore_changes = [
      properties["db_edition"],
      cidr,
      admin_password,
      network,
      terraform_labels
    ]
  }

}