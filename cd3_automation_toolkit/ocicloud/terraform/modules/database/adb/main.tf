# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Autonomous database
## Create autonomous database
################################

resource "oci_database_autonomous_database" "autonomous_database" {
    #Required
    compartment_id = var.compartment_id

    #Optional
    admin_password = var.admin_password
    are_primary_whitelisted_ips_used = var.are_primary_whitelisted_ips_used != null ? var.are_primary_whitelisted_ips_used : null
    auto_refresh_frequency_in_seconds = var.auto_refresh_frequency_in_seconds != null ? var.auto_refresh_frequency_in_seconds : null
    auto_refresh_point_lag_in_seconds = var.auto_refresh_point_lag_in_seconds != null ? var.auto_refresh_point_lag_in_seconds : null
    autonomous_container_database_id = var.autonomous_container_database_id != null ? var.autonomous_container_database_id : null
    autonomous_database_backup_id = var.autonomous_database_source_backup_id != null ? ((var.adb_source != null && var.adb_source == "BACKUP_FROM_ID")? var.autonomous_database_source_backup_id:null) : null
    autonomous_database_id = var.autonomous_database_id != null ? ((var.adb_source != null && var.adb_source == "BACKUP_FROM_TIMESTAMP")? var.autonomous_database_id:null) : null
    autonomous_maintenance_schedule_type = var.autonomous_maintenance_schedule_type != null ? var.autonomous_maintenance_schedule_type: null
    backup_retention_period_in_days = var.backup_retention_period_in_days != null ? var.backup_retention_period_in_days : null
    character_set = var.character_set != null ? var.character_set : null
    compute_count = var.compute_count
    compute_model = var.compute_model
    dynamic "customer_contacts" {
      for_each = var.customer_contacts!=null ? (var.customer_contacts[0] != "" ? var.customer_contacts : []) : []

      content {
        email = customer_contacts.value
      }
    }
    data_safe_status = var.data_safe_status != null ? var.data_safe_status: null
    data_storage_size_in_gb = var.data_storage_size_in_gb != null ? var.data_storage_size_in_gb: null
    data_storage_size_in_tbs = var.data_storage_size_in_tbs != null ? var.data_storage_size_in_tbs : null
    database_edition = var.database_edition
    db_name = var.db_name
    db_version = var.db_version
    db_workload = var.db_workload
    defined_tags = var.defined_tags
    disaster_recovery_type = var.disaster_recovery_type != null ? var.disaster_recovery_type : null
    display_name = var.display_name
    dynamic "encryption_key" {
      for_each = (var.kms_key_id != null && var.vault_id != null) ? [1] : []

      content {
        kms_key_id = var.kms_key_id
        vault_id   = var.vault_id
      }
    }
    freeform_tags = var.freeform_tags
    in_memory_percentage = var.in_memory_percentage != null ? var.in_memory_percentage : null
    is_auto_scaling_enabled = var.is_auto_scaling_enabled != null ? var.is_auto_scaling_enabled : null
    is_auto_scaling_for_storage_enabled = var.is_auto_scaling_for_storage_enabled != null ? var.is_auto_scaling_for_storage_enabled : null
    is_backup_retention_locked = var.is_backup_retention_locked != null ? var.is_backup_retention_locked : null
    is_dedicated = var.is_dedicated != null ? var.is_dedicated : null
    is_local_data_guard_enabled = var.is_local_data_guard_enabled != null ? var.is_local_data_guard_enabled : null
    is_mtls_connection_required = var.is_mtls_connection_required != null ? var.is_mtls_connection_required : null
    is_replicate_automatic_backups = var.is_replicate_automatic_backups != null ? var.is_replicate_automatic_backups : null
    kms_key_id = var.kms_key_id != null ? var.kms_key_id : null
    license_model = var.license_model
    ncharacter_set = var.ncharacter_set
    nsg_ids = length(var.network_security_group_ids) != 0 ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : null
    ocpu_count = var.ocpu_count != null ? var.ocpu_count : null
    private_endpoint_ip = var.private_endpoint_ip != null ? var.private_endpoint_ip : null
    private_endpoint_label = var.private_endpoint_label != null? var.private_endpoint_label : null
    refreshable_mode = var.refreshable_mode != null ? var.refreshable_mode : null
    remote_disaster_recovery_type = var.remote_disaster_recovery_type!= null? var.remote_disaster_recovery_type : null
    secret_id = var.secret_id != null ? var.secret_id: null
    secret_version_number = var.secret_version_number != null ? var.secret_version_number : null
    vault_id = var.vault_id != null ? var.vault_id : null
    source = var.adb_source != null ? var.adb_source : null
    source_id = var.source_id != null ? var.source_id: null
    standby_whitelisted_ips = var.standby_whitelisted_ips != null ? var.standby_whitelisted_ips : null
    subnet_id = var.subnet_id
    subscription_id = var.subscription_id != null ? var.subscription_id : null
    time_of_auto_refresh_start = var.time_of_auto_refresh_start != null ? var.time_of_auto_refresh_start : null
    timestamp = var.timestamp != null ? var.timestamp : null
    use_latest_available_backup_time_stamp = var.use_latest_available_backup_time_stamp != null ? var.use_latest_available_backup_time_stamp : null

    whitelisted_ips = var.whitelisted_ips != null ?var.whitelisted_ips: null
    lifecycle {
    ignore_changes = [
       /* source,
      admin_password,
      character_set,
      compute_count,
      compute_model,
      customer_contacts,
      data_storage_size_in_tbs,
      disaster_recovery_type,
      encryption_key,                   # This ignores the entire nested block
      in_memory_percentage,
      is_auto_scaling_enabled,
      is_auto_scaling_for_storage_enabled,
      is_backup_retention_locked,
      is_dedicated,
      is_local_data_guard_enabled,
      is_mtls_connection_required,
      is_replicate_automatic_backups,
      kms_key_id,
      ocpu_count,
      private_endpoint_ip,
      private_endpoint_label,
      refreshable_mode,
      remote_disaster_recovery_type,
      secret_id,
      secret_version_number,
      vault_id,
        source_id,
      standby_whitelisted_ips,
      subscription_id,
      time_of_auto_refresh_start,
      timestamp,
      use_latest_available_backup_time_stamp,*/
    ]
  }
}