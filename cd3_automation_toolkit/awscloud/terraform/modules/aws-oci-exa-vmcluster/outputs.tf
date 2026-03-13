# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
###############################################
## Outputs Block - Oracle ExaVM Cluster @AWS
## Create Oracle ExaVM Cluster @AWS
###############################################

output "vm_cluster_id" {
  value = aws_odb_cloud_vm_cluster.vm_cluster.id
}

output "vm_cluster_status" {
  value = aws_odb_cloud_vm_cluster.vm_cluster.status
}

output "scan_dns_name" {
  value = aws_odb_cloud_vm_cluster.vm_cluster.scan_dns_name
}