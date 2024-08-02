# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Outputs Block - Nodepool
# Create Nodepool and nodes
############################

output "nodepool_tf_id" {
  value = oci_containerengine_node_pool.nodepool.id
}