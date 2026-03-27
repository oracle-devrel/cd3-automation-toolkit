# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##########################################
## Outputs Block - Oracle ExaInfra @AWS
## Create Oracle ExaInfra @AWS
##########################################

output "infrastructure_id" {
  description = "Exadata Infrastructure ID"
  value       = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.id
}

output "infrastructure_status" {
  description = "Infrastructure lifecycle state"
  value       = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.status
}

output "db_server_ids" {
  description = "List of DB server IDs for VM Cluster creation"
  value       = data.aws_odb_db_servers.exadata_infrastructure.db_servers[*].id
}

output "vm_cluster_prerequisites" {
  description = "All prerequisites needed for VM Cluster creation"
  value = {
    infrastructure_id    = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.id
    db_server_ids        = data.aws_odb_db_servers.exadata_infrastructure.db_servers[*].id
    availability_zone    = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.availability_zone
    availability_zone_id = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.availability_zone_id
    region               = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.region
  }
}