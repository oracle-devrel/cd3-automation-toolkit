# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################################
## Resource Block - Oracle ExaVM Cluster @GCP
## Create Oracle ExaVM Cluster @GCP
################################################

resource "google_compute_network" "vpc_network" {

  count                   = var.cluster_config.create_odb_network ? 1 : 0
  name                    = var.cluster_config.vpc_network_name
  project                 = var.cluster_config.project
  auto_create_subnetworks = false # Sets the VPC to "Custom" mode
  mtu                     = 1460
}


# Create ODB Network
resource "google_oracle_database_odb_network" "odb_network" {

  count           = var.cluster_config.create_odb_network ? 1 : 0
  odb_network_id  = var.cluster_config.odb_network_id
  location        = var.cluster_config.location
  project         = var.cluster_config.project
  network         = google_compute_network.vpc_network[0].id
  gcp_oracle_zone = var.cluster_config.odb_network_gcp_oracle_zone
  labels          = var.labels
  #deletion_protection = "false"
}

# Create ODB Network Subnets
resource "google_oracle_database_odb_subnet" "odb_client_subnet" {

  count         = var.cluster_config.create_odb_network ? 1 : 0
  odb_subnet_id = var.cluster_config.odb_client_subnet_id
  location      = var.cluster_config.location
  project       = var.cluster_config.project
  odbnetwork    = google_oracle_database_odb_network.odb_network[0].odb_network_id
  cidr_range    = var.cluster_config.client_subnet_cidr
  purpose       = "CLIENT_SUBNET"
  labels        = var.labels
  #deletion_protection = "false"
}
resource "google_oracle_database_odb_subnet" "odb_backup_subnet" {

  count         = var.cluster_config.create_odb_network ? 1 : 0
  odb_subnet_id = var.cluster_config.odb_backup_subnet_id
  location      = var.cluster_config.location
  project       = var.cluster_config.project
  odbnetwork    = google_oracle_database_odb_network.odb_network[0].odb_network_id
  cidr_range    = var.cluster_config.backup_subnet_cidr
  purpose       = "BACKUP_SUBNET"
  labels        = var.labels
  #deletion_protection = "false"
}

# Create Exadata VM Cluster
resource "google_oracle_database_cloud_vm_cluster" "vm_cluster" {

  location               = var.cluster_config.location
  project                = var.cluster_config.project
  exadata_infrastructure = var.exadata_infrastructure_id
  display_name           = var.cluster_config.display_name
  cloud_vm_cluster_id    = var.cluster_config.cloud_vm_cluster_id
  odb_network            = var.cluster_config.create_odb_network == true ? google_oracle_database_odb_network.odb_network[0].id : "projects/${var.cluster_config.project}/locations/${var.cluster_config.location}/odbNetworks/${var.cluster_config.odb_network_id}"
  odb_subnet             = var.cluster_config.create_odb_network == true ? google_oracle_database_odb_subnet.odb_client_subnet[0].id : "projects/${var.cluster_config.project}/locations/${var.cluster_config.location}/odbNetworks/${var.cluster_config.odb_network_id}/odbSubnets/${var.cluster_config.odb_client_subnet_id}"
  backup_odb_subnet      = var.cluster_config.create_odb_network == true ? google_oracle_database_odb_subnet.odb_backup_subnet[0].id : "projects/${var.cluster_config.project}/locations/${var.cluster_config.location}/odbNetworks/${var.cluster_config.odb_network_id}/odbSubnets/${var.cluster_config.odb_backup_subnet_id}"
  properties {
    # cluster_name                = "pq-ppat4"
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
      diagnostics_events_enabled = var.cluster_config.diagnostics_data_collection_options.diagnostics_events_enabled
      health_monitoring_enabled  = var.cluster_config.diagnostics_data_collection_options.health_monitoring_enabled
      incident_logs_enabled      = var.cluster_config.diagnostics_data_collection_options.incident_logs_enabled
    }
    time_zone {
      id = var.cluster_config.time_zone
    }
    scan_listener_port_tcp = var.cluster_config.scan_listener_port_tcp
    # scan_listener_port_tcp_ssl  = 2484
  }
  labels = var.labels

  #deletion_protection = "false"
  lifecycle {
    ignore_changes = [
      properties[0].db_server_ocids,
      properties[0].cpu_core_count,
      properties[0].memory_size_gb,
      properties[0].db_node_storage_size_gb,
      properties[0].data_storage_size_tb,
      properties[0].local_backup_enabled,
      properties[0].sparse_diskgroup_enabled
    ]
  }
}



# Output OCID of Exadata VM Cluster
output "oci_exa_vm_cluster_ocid" {
  value = google_oracle_database_cloud_vm_cluster.vm_cluster.properties[0].ocid
}