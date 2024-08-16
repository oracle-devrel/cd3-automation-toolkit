# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Network
# Create Route Table
############################

output "route_table_ids" {
  value = one(concat(oci_core_route_table.route_table.*.id,oci_core_default_route_table.default_route_table.*.id))
  #value = concat(oci_core_route_table.route_table.*.id,oci_core_default_route_table.default_route_table.*.id)[0]
}

