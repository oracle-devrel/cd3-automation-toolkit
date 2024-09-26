# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Output Block - Network
# Create DRG Route Distribution Statement
############################################

output "drg_route_distribution_statement_tf_id" {
  value = oci_core_drg_route_distribution_statement.drg_route_distribution_statement.id
}
