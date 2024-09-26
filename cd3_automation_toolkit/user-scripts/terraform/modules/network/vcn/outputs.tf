# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Network
# Create VCNs
############################

output "vcn_tf_id" {
  value = oci_core_vcn.vcn.id
}

output "vcn_default_dhcp_id" {
  value = oci_core_vcn.vcn.default_dhcp_options_id
}

output "vcn_default_security_list_id" {
  value = oci_core_vcn.vcn.default_security_list_id
}

output "vcn_default_route_table_id" {
  value = oci_core_vcn.vcn.default_route_table_id
}
