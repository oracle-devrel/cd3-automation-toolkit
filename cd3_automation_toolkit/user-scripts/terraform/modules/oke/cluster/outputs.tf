// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Cluster
# Create Cluster
############################

output "cluster_tf_id" {
  value = oci_containerengine_cluster.cluster.id
}