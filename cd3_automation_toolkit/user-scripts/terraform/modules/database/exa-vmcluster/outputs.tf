# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Outputs Block - Database
# Create ExaVMClusters
############################

output "exa_vmcluster_tf_id" {
  value = oci_database_cloud_vm_cluster.exa_vmcluster.id
}