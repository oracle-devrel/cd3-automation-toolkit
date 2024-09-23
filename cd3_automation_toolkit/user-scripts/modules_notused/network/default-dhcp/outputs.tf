# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Network
# Create Default DHCP Options
############################


output "default_dhcp_tf_id" {
  value = oci_core_default_dhcp_options.default_dhcp_option.id
}