// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create DRG Route Distribution
############################

output "drg_route_distribution_tf_id" {
  value = oci_core_drg_route_distribution.drg_route_distribution.id
}
