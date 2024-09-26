# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Outputs Block - DNS Zone #
############################

output "dns_zone_id" {
  value = oci_dns_zone.zone.id
}
output "dns_zone_name" {
  value = oci_dns_zone.zone.name
}