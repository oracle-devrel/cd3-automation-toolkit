# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Network
# Create Custom DHCP Options
############################

output "custom_dhcp_tf_id" {
  value = oci_core_dhcp_options.custom_dhcp_option.id
}