// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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