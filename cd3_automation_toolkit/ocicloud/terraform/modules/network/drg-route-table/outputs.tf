# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Network
# Create DRG Route Table
############################

output "drg_route_table_tf_id" {
  value = oci_core_drg_route_table.drg_route_table.id
}
