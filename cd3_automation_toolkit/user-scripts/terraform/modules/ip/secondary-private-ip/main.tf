# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Secondary Private IP
## Create Secondary Private IP
################################

resource "oci_core_private_ip" "private_ip" {

  #Optional
  defined_tags   = var.defined_tags
  display_name   = var.display_name
  freeform_tags  = var.freeform_tags
  hostname_label = var.hostname_label
  ip_address     = var.ip_address
  vlan_id        = var.vlan_id
  vnic_id        = var.vnic_id

}