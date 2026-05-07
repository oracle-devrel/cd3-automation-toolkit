# ========================================
# Root Module - Oracle ExaData @AWS
# ========================================

# --------------------------------------------------
# STEP 1: Create ODB Networks (and optional peering)
# Peering is handled inside the module via create_odb_peering flag.
# --------------------------------------------------
module "odb_network" {
  source   = "./modules/aws-odb-network"
  for_each = var.odb_networks_config

  network_key    = each.key
  network_config = each.value
}

# --------------------------------------------------
# STEP 2: Deploy Exadata Infrastructure(s)
# --------------------------------------------------
module "exadata_infrastructure" {
  source   = "./modules/aws-oci-exa-infra"
  for_each = var.aws_oci_exa_infra

  infra_config = each.value
  infra_key    = each.key
  tags         = each.value.tags
}

# --------------------------------------------------
# STEP 3: Deploy VM Cluster(s)
#
# created_odb_network_id:
#   create_odb_network = true  → resolved from module.odb_network using odb_network_name as key
#   create_odb_network = false → null (vmcluster module does display_name lookup instead)
# --------------------------------------------------
module "vm_cluster" {
  source   = "./modules/aws-oci-exa-vmcluster"
  for_each = var.aws_oci_exa_vmclusters

  cluster_config     = each.value
  cluster_key        = each.key
  tags               = each.value.tags
  create_odb_network = each.value.create_odb_network
  created_odb_network_id = (
    each.value.create_odb_network
    ? module.odb_network[each.value.odb_network_name].odb_network_id
    : null
  )

  depends_on = [
    module.exadata_infrastructure,
    module.odb_network,
  ]
}

# ========================================
# Outputs
# ========================================

output "odb_network_ids" {
  description = "Created ODB network IDs"
  value       = { for k, v in module.odb_network : k => v.odb_network_id }
}

output "odb_network_statuses" {
  description = "Created ODB network statuses"
  value       = { for k, v in module.odb_network : k => v.odb_network_status }
}

output "odb_peering_ids" {
  description = "Created ODB peering IDs per network (null when create_odb_peering = false)"
  value       = { for k, v in module.odb_network : k => v.odb_peering_id }
}

output "odb_peering_statuses" {
  description = "Created ODB peering statuses per network (null when create_odb_peering = false)"
  value       = { for k, v in module.odb_network : k => v.odb_peering_status }
}

output "infrastructure_ids" {
  description = "Exadata Infrastructure IDs"
  value       = { for k, v in module.exadata_infrastructure : k => v.infrastructure_id }
}

output "infrastructure_status" {
  description = "Exadata Infrastructure statuses"
  value       = { for k, v in module.exadata_infrastructure : k => v.infrastructure_status }
}

output "db_server_ids" {
  description = "DB Server IDs per infrastructure"
  value       = { for k, v in module.exadata_infrastructure : k => v.db_server_ids }
}

output "vm_cluster_ids" {
  description = "VM Cluster IDs"
  value       = { for k, v in module.vm_cluster : k => v.vm_cluster_id }
}

output "vm_cluster_states" {
  description = "VM Cluster statuses"
  value       = { for k, v in module.vm_cluster : k => v.vm_cluster_status }
}

output "vm_clusters_summary" {
  description = "VM Cluster summary"
  value = {
    for k, v in module.vm_cluster : k => {
      id            = v.vm_cluster_id
      status        = v.vm_cluster_status
      scan_dns_name = v.scan_dns_name
    }
  }
}
