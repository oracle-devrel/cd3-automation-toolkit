// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Custom DHCP Options
############################

output "custom_dhcp_tf_id" {
  value = oci_core_dhcp_options.custom_dhcp_option.id
}