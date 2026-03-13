# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################################
## Resource Block - Oracle ExaVM Cluster @AWS
## Create Oracle ExaVM Cluster @AWS
################################################

data "aws_odb_cloud_exadata_infrastructures" "all" {}
data "aws_odb_networks" "all" {}

locals {
  infra_id = [for i in data.aws_odb_cloud_exadata_infrastructures.all.cloud_exadata_infrastructures : i.id if i.display_name == var.cluster_config.exadata_infrastructure_name][0]
  net_id   = [for n in data.aws_odb_networks.all.odb_networks : n.id if n.display_name == var.cluster_config.odb_network_name][0]
}

data "aws_odb_db_servers" "exa_db_servers" {
  cloud_exadata_infrastructure_id = local.infra_id
}

resource "aws_odb_cloud_vm_cluster" "vm_cluster" {
  # ──────────────────────────────────────────────────────────────────────
  # MANDATORY: Required for provisioning
  # ──────────────────────────────────────────────────────────────────────
  cloud_exadata_infrastructure_id = local.infra_id
  odb_network_id                  = local.net_id
  db_servers                      = data.aws_odb_db_servers.exa_db_servers.db_servers[*].id

  display_name                = var.cluster_config.display_name
  cluster_name                = var.cluster_config.cluster_name
  gi_version                  = var.cluster_config.gi_version
  hostname_prefix             = var.cluster_config.hostname_prefix
  region                      = var.cluster_config.region
  cpu_core_count              = var.cluster_config.cpu_core_count
  memory_size_in_gbs          = var.cluster_config.memory_size_in_gbs
  data_storage_size_in_tbs    = var.cluster_config.data_storage_size_in_tbs
  db_node_storage_size_in_gbs = var.cluster_config.db_node_storage_size_in_gbs
  ssh_public_keys             = var.cluster_config.ssh_public_keys

  # ──────────────────────────────────────────────────────────────────────
  # IMMUTABLE: (Changing these triggers resource replacement)
  # ──────────────────────────────────────────────────────────────────────
  is_local_backup_enabled     = var.cluster_config.is_local_backup_enabled
  is_sparse_diskgroup_enabled = var.cluster_config.is_sparse_diskgroup_enabled

  # ──────────────────────────────────────────────────────────────────────
  # OPTIONAL: Customizable with defaults
  # ──────────────────────────────────────────────────────────────────────
  license_model          = var.cluster_config.license_model
  timezone               = var.cluster_config.timezone
  scan_listener_port_tcp = var.cluster_config.scan_listener_port_tcp

  data_collection_options {
    is_diagnostics_events_enabled = var.cluster_config.data_collection_options.is_diagnostics_events_enabled
    is_health_monitoring_enabled  = var.cluster_config.data_collection_options.is_health_monitoring_enabled
    is_incident_logs_enabled      = var.cluster_config.data_collection_options.is_incident_logs_enabled
  }

  #  Tagging
  tags = var.tags

  timeouts {
    create = var.cluster_config.timeout_create
    update = var.cluster_config.timeout_update
    delete = var.cluster_config.timeout_delete
  }
}