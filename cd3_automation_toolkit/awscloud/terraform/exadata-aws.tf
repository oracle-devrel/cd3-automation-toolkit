# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##################################
# Module Block - Exa @AWS
# Create Exa Infra and VM Cluster
##################################

module "exa-infra-aws" {
  source   = "./modules/aws-oci-exa-infra"
  for_each = var.aws_oci_exa_infra

  infra_config = each.value
  infra_key    = each.key
  tags         = each.value.tags
}

module "exa-vmcluster-aws" {
  source   = "./modules/aws-oci-exa-vmcluster"
  for_each = var.aws_oci_exa_vmclusters

  cluster_config = each.value
  cluster_key    = each.key
  tags           = each.value.tags
}


# ========================================
# Root - Outputs
# ========================================

output "aws_oci_exa_infra" {
  description = "Map of all Exadata Infrastructure details"
  value       = module.exa-infra-aws.aws_oci_exa_infra
}

output "db_servers" {
  description = "Map of DB server IDs for each infrastructure"
  value       = module.exa-infra-aws.db_servers
}

output "db_servers_details" {
  description = "Map of detailed DB server information for each infrastructure"
  value       = module.exa-infra-aws.db_servers_details
}

output "db_servers_count" {
  description = "Map of DB server counts for each infrastructure"
  value       = module.exa-infra-aws.db_servers_count
}

output "vm_cluster_prerequisites" {
  description = "Map of VM Cluster prerequisites for each infrastructure"
  value       = module.exa-infra-aws.vm_cluster_prerequisites
}

output "vm_cluster_ids" {
  description = "VM Cluster IDs"
  value       = { for k, v in module.exa-vmcluster-aws : k => v.vm_cluster_id }
}

output "vm_cluster_states" {
  description = "VM Cluster statuses"
  value       = { for k, v in module.exa-vmcluster-aws : k => v.vm_cluster_status }
}

output "vm_clusters_summary" {
  description = "Complete summary of all VM Clusters"
  value = {
    for k, v in module.exa-vmcluster-aws : k => {
      id            = v.vm_cluster_id
      status        = v.vm_cluster_status
      scan_dns_name = v.scan_dns_name
    }
  }
}
