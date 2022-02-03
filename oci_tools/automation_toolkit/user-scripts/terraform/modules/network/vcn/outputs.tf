// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create VCNs
############################

output "vcn_id" {
  value = zipmap(oci_core_vcn.vcn.*.display_name, oci_core_vcn.vcn.*.id)
}

output "ads" {
  value = data.oci_identity_availability_domains.demo_availability_domains.availability_domains.*.name
}

output "vcn_default_dhcp_id" {
  value = zipmap(oci_core_vcn.vcn.*.display_name, oci_core_vcn.vcn.*.default_dhcp_options_id)
}

output "vcn_default_security_list_id" {
  value = zipmap(oci_core_vcn.vcn.*.display_name, oci_core_vcn.vcn.*.default_security_list_id)
}
