# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
output "service-list_tf_id" {
  value = oci_network_firewall_network_firewall_policy_service_list.network_firewall_policy_service_list.id
}