# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

##################################
# Module Block - Exa @GCP
# Create Exa Infra and VM Cluster
##################################

module "exa-infra-gcp" {
  source   = "./modules/gcp-oci-exa-infra"
  for_each = var.gcp_oci_exa_infra

  infra_config = each.value
  labels       = each.value.labels
}


data "google_oracle_database_db_servers" "this" {
  depends_on = [module.exa-infra-gcp]
  for_each                     = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location                     = each.value.location
  project                      = each.value.project
  cloud_exadata_infrastructure = each.value.exadata_infrastructure_id
  #location                     = "us-east4"
  #cloud_exadata_infrastructure = "exadev"
}

data "google_oracle_database_cloud_exadata_infrastructure" "exa_infra" {
  depends_on = [module.exa-infra-gcp]
  for_each                        = var.gcp_oci_exa_vmclusters != null ? var.gcp_oci_exa_vmclusters : {}
  location                        = each.value.location
  project                         = each.value.project
  cloud_exadata_infrastructure_id = each.value.exadata_infrastructure_id
  #location                        = "us-east4"
  #cloud_exadata_infrastructure_id = "exadev"
}

output "db_servers" {
  description = "DB Servers"
  value       = data.google_oracle_database_db_servers.this.db_servers[*].properties.0.ocid
}

output "exa_infra_id" {
  description = "DB Servers"
  value       = data.google_oracle_database_cloud_exadata_infrastructure.exa_infra.id
}




module "exa-vmcluster-gcp" {
  source   = "./modules/gcp-oci-exa-vmcluster"
  for_each = var.gcp_oci_exa_vmclusters

  cluster_config            = each.value
  db_server_ocids           = data.google_oracle_database_db_servers.this[each.key].db_servers[*].properties.0.ocid
  exadata_infrastructure_id = data.google_oracle_database_cloud_exadata_infrastructure.exa_infra[eah.key].id
  labels                    = each.value.labels
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
