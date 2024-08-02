// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
output "firewall_tf_id" {
  value = oci_network_firewall_network_firewall.network_firewall.id
}

