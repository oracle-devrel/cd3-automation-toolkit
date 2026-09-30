# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Reserved Private IP
## Create Reserved Private IP
################################

resource "oci_core_private_ip" "private_ip" {

  lifetime  = var.lifetime
  subnet_id = length(regexall("ocid1.subnet.oc*", var.subnet_id)) > 0 ? var.subnet_id : one(data.oci_core_subnets.oci_subnet.subnets[*].id)
  #Optional
  defined_tags   = var.defined_tags
  display_name   = var.display_name
  freeform_tags  = var.freeform_tags
  hostname_label = var.hostname_label
  ip_address     = var.ip_address
  vlan_id        = var.vlan_id
  vnic_id        = var.vnic_id

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], vnic_id, vlan_id]
  }
}