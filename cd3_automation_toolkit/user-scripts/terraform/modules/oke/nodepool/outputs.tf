// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Nodepool
# Create Nodepool and nodes
############################

output "nodepool_tf_id" {
  value = oci_containerengine_node_pool.nodepool.id
}