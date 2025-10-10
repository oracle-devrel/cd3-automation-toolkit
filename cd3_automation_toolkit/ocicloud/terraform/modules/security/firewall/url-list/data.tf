# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
/*locals {
  policy_ocid = data.oci_network_firewall_network_firewall_policies.fw-policy.network_firewall_policy_summary_collection[*].id

}
data "oci_network_firewall_network_firewall_policies" "fw-policy" {
  compartment_id = var.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", var.compartment_id)) > 0 ? var.compartment_id : var.compartment_ocids[var.compartment_id]) : var.compartment_ocids[var.compartment_id]
  display_name   = var.network_firewall_policy_id
*/