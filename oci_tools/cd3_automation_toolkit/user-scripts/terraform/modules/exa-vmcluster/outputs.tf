// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Database
# Create ExaVMClusters
############################

output "exa_vmcluster_tf_id" {
  value = oci_database_cloud_vm_cluster.exa_vmcluster.id
}