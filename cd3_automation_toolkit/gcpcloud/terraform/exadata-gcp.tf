# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

##################################
# Module Block - Exa @GCP
# Create Exa Infra and VM Cluster
##################################

module "exa-infra-gcp" {
  source   = "./modules/gcp-oci-exa-infra"
  for_each = var.gcp_oci_exa_infra != null ? var.gcp_oci_exa_infra : {}

  infra_config = each.value
  labels       = each.value.labels
}


data "google_oracle_database_db_servers" "this" {
  depends_on                   = [module.exa-infra-gcp]
  for_each                     = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location                     = each.value.location
  project                      = each.value.exadata_infrastructure_project
  cloud_exadata_infrastructure = each.value.exadata_infrastructure_id
}

output "db_servers" {
  description = "DB Servers"
  value       = { for k, v in var.gcp_oci_exa_vmclusters : k => data.google_oracle_database_db_servers.this[k].db_servers[*].properties.0.ocid }
}


/*
data "google_oracle_database_cloud_exadata_infrastructure" "exa_infra" {
  depends_on                      = [module.exa-infra-gcp]
  for_each                        = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location                        = each.value.location
  project                         = each.value.project
  cloud_exadata_infrastructure_id = each.value.exadata_infrastructure_id
}
output "exa_infra_id" {
  description = "DB Servers"
  value       = { for k, v in var.gcp_oci_exa_vmclusters : k => data.google_oracle_database_cloud_exadata_infrastructure.exa_infra[k].id }
}




data "google_oracle_database_odb_network" "gcp_odb_network" {
  depends_on = [module.gcp_network]
  for_each                          = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location = each.value.location
  odb_network_id = each.value.odb_network_id
}

data "google_oracle_database_odb_subnet" "gcp_client_subnet" {

  depends_on = [module.gcp_network]
  for_each                          = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location = each.value.location
  odb_network_id = each.value.odb_network_id
  odb_subnet_id = each.value.odb_client_subnet_id
}

data "google_oracle_database_odb_subnet" "gcp_backup_subnet" {

  depends_on = [module.gcp_network]
  for_each                          = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location = each.value.location
  odb_network_id = each.value.odb_network_id
  odb_subnet_id = each.value.odb_backup_subnet_id
}
*/


module "exa-vmcluster-gcp" {

  depends_on = [module.gcp_network, module.exa-infra-gcp]
  source     = "./modules/gcp-oci-exa-vmcluster"
  for_each   = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}

  cluster_config  = each.value
  db_server_ocids = data.google_oracle_database_db_servers.this[each.key].db_servers[*].properties.0.ocid
  #exadata_infrastructure_id = data.google_oracle_database_cloud_exadata_infrastructure.exa_infra[each.key].id
  exadata_infrastructure_id = "projects/${each.value.exadata_infrastructure_project}/locations/${each.value.location}/cloudExadataInfrastructures/${each.value.exadata_infrastructure_id}"
  odb_network_id            = "projects/${each.value.odb_network_project}/locations/${each.value.location}/odbNetworks/${each.value.odb_network_id}"
  odb_client_subnet_id      = "projects/${each.value.odb_network_project}/locations/${each.value.location}/odbNetworks/${each.value.odb_network_id}/odbSubnets/${each.value.odb_client_subnet_id}"
  odb_backup_subnet_id      = "projects/${each.value.odb_network_project}/locations/${each.value.location}/odbNetworks/${each.value.odb_network_id}/odbSubnets/${each.value.odb_backup_subnet_id}"

  /*
  odb_network_id            = each.value.create_odb_network == true ? data.google_oracle_database_odb_network.gcp_odb_network[each.key].id : "projects/${var.cluster_config.odb_network_project}/locations/${var.cluster_config.location}/odbNetworks/${var.cluster_config.odb_network_id}"
  odb_client_subnet_id = each.value.create_odb_network_subnets == true ? data.google_oracle_database_odb_subnet.gcp_client_subnet[each.key].id
  odb_backup_subnet_id =
  */

  labels = each.value.labels
}

/*
# ========================================
# Root - Outputs
# ========================================

output "gcp_oci_exa_infra" {
  description = "Map of all Exadata Infrastructure details"
  value       = module.exadata_infrastructure.gcp_oci_exa_infra
}

output "db_servers" {
  description = "Map of DB server IDs for each infrastructure"
  value       = module.exadata_infrastructure.db_servers
}

output "db_servers_details" {
  description = "Map of detailed DB server information for each infrastructure"
  value       = module.exadata_infrastructure.db_servers_details
}

output "db_servers_count" {
  description = "Map of DB server counts for each infrastructure"
  value       = module.exadata_infrastructure.db_servers_count
}

output "vm_cluster_prerequisites" {
  description = "Map of VM Cluster prerequisites for each infrastructure"
  value       = module.exadata_infrastructure.vm_cluster_prerequisites
}

# ========================================
# Root Module - ./outputs.tf
# ========================================

output "vm_cluster_ids" {
  description = "VM Cluster IDs"
  value       = { for k, v in module.vm_cluster : k => v.vm_cluster_id }
}

output "vm_cluster_states" {
  description = "VM Cluster statuses"
  value       = { for k, v in module.vm_cluster : k => v.vm_cluster_status }
}

output "vm_clusters_summary" {
  description = "Complete summary of all VM Clusters"
  value = {
    for k, v in module.vm_cluster : k => {
      id            = v.vm_cluster_id
      status        = v.vm_cluster_status
      scan_dns_name = v.scan_dns_name
    }
  }
}
*/
