// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Database
# Create ExaVMClusters
############################

resource "oci_database_cloud_vm_cluster" "exa_vmcluster" {
  #Required
  subnet_id                       = var.cluster_subnet_id
  backup_subnet_id                = var.backup_subnet_id
  cloud_exadata_infrastructure_id = var.exadata_infrastructure_id
  compartment_id                  = var.compartment_id
  cpu_core_count                  = var.cpu_core_count
  display_name                    = var.display_name
  gi_version                      = var.gi_version
  hostname                        = var.hostname
  ssh_public_keys                 = [var.ssh_public_keys]

  #Optional
  backup_network_nsg_ids      = var.backup_network_nsg_ids
  cluster_name                = var.cluster_name
  data_storage_percentage     = var.data_storage_percentage
  defined_tags                = var.defined_tags
  domain                      = var.domain
  freeform_tags               = var.freeform_tags
  is_local_backup_enabled     = var.is_local_backup_enabled
  is_sparse_diskgroup_enabled = var.is_sparse_diskgroup_enabled
  license_model               = var.license_model
  nsg_ids                     = var.nsg_ids
  ocpu_count                  = var.ocpu_count
  scan_listener_port_tcp      = var.scan_listener_port_tcp
  scan_listener_port_tcp_ssl  = var.scan_listener_port_tcp_ssl
  time_zone                   = var.time_zone
}