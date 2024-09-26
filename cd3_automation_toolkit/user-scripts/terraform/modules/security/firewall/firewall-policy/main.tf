# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall_policy" "network_firewall_policy" {
  compartment_id = var.compartment_id
  display_name = var.display_name
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"],defined_tags["SE_Details.SE_Name"]]
  }

}

