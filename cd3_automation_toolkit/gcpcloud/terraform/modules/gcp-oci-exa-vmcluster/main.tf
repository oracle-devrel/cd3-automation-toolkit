# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################################
## Resource Block - Oracle ExaVM Cluster @GCP
## Create Oracle ExaVM Cluster @GCP
################################################



# Create Exadata VM Cluster
resource "google_oracle_database_cloud_vm_cluster" "vm_cluster" {
  location               = var.cluster_config.location
  project                = var.cluster_config.project
  exadata_infrastructure = var.exadata_infrastructure_id
  display_name           = var.cluster_config.display_name
  cloud_vm_cluster_id    = var.cluster_config.cloud_vm_cluster_id
  odb_network            = var.odb_network_id
  odb_subnet             = var.odb_client_subnet_id
  backup_odb_subnet      = var.odb_backup_subnet_id
  properties {
    gi_version               = var.cluster_config.gi_version
    db_server_ocids          = var.db_server_ocids
    cpu_core_count           = var.cluster_config.cpu_core_count
    memory_size_gb           = var.cluster_config.memory_size_gb
    db_node_storage_size_gb  = var.cluster_config.db_node_storage_size_gb
    data_storage_size_tb     = var.cluster_config.data_storage_size_tb
    node_count               = var.cluster_config.node_count
    ocpu_count               = var.cluster_config.ocpu_count
    disk_redundancy          = var.cluster_config.disk_redundancy
    local_backup_enabled     = var.cluster_config.local_backup_enabled
    sparse_diskgroup_enabled = var.cluster_config.sparse_diskgroup_enabled
    cluster_name             = var.cluster_config.cluster_name
    hostname_prefix          = var.cluster_config.hostname_prefix
    ssh_public_keys          = var.cluster_config.ssh_public_keys
    license_type             = var.cluster_config.license_type
    diagnostics_data_collection_options {
      diagnostics_events_enabled = var.cluster_config.diagnostics_data_collection_options != null ? var.cluster_config.diagnostics_data_collection_options.diagnostics_events_enabled : true
      health_monitoring_enabled  = var.cluster_config.diagnostics_data_collection_options != null ? var.cluster_config.diagnostics_data_collection_options.health_monitoring_enabled : true
      incident_logs_enabled      = var.cluster_config.diagnostics_data_collection_options != null ? var.cluster_config.diagnostics_data_collection_options.incident_logs_enabled : true
    }
    time_zone {
      id = var.cluster_config.time_zone
    }
    #scan_listener_port_tcp = var.cluster_config.scan_listener_port_tcp
  }
  # Labels are not getting applied to oracle resources
  labels = var.labels

  timeouts {
    create = "12h"
    update = "2h"
    delete = "8h"
  }

  #deletion_protection = "false"
  lifecycle {
    ignore_changes = [
      properties[0].db_server_ocids,
      properties[0].cpu_core_count,
      properties[0].memory_size_gb,
      properties[0].db_node_storage_size_gb,
      properties[0].data_storage_size_tb,
      properties[0].local_backup_enabled,
      properties[0].sparse_diskgroup_enabled,
      properties[0].ssh_public_keys
    ]
  }
}



# Output OCID of Exadata VM Cluster
output "oci_exa_vm_cluster_ocid" {
  value = google_oracle_database_cloud_vm_cluster.vm_cluster.properties[0].ocid
}