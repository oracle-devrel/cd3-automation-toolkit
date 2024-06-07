// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Nodepool
# Create Nodepool and nodes
############################

output "virtual_nodepool_tf_id" {
  value = oci_containerengine_virtual_node_pool.virtual_nodepool.id
}