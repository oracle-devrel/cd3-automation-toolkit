// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Backend
#######################################

resource "oci_network_load_balancer_backend" "backend" {
  #Required
  backend_set_name         = var.backend_set_name
  network_load_balancer_id = var.network_load_balancer_id
  port                     = var.port

  #Optional
  ip_address = var.ip_address != "" ? (length(regexall("IP:", var.ip_address)) > 0 ? split("IP:", var.ip_address)[1] : data.oci_core_instance.nlb_instance_ip[0].private_ip) : null
  is_drain   = var.is_drain
  is_offline = var.is_offline
  name       = length(regexall("IP:", var.ip_address)) > 0 ? join(":", [split("IP:", var.ip_address)[1], var.port]) : join(":", [merge(local.nlb_private_ip_ocid.private_ocids.*...)[merge(local.nlb_instance_vnic_ocid.vnic_ocids.*...)[merge(local.nlb_instance_ocid.ocid.*...)[split("NAME:", var.ip_address)[1]][0]][0]][0], var.port])
  target_id  = length(regexall("IP:*", var.ip_address)) == 0 ? merge(local.nlb_private_ip_ocid.private_ocids.*...)[merge(local.nlb_instance_vnic_ocid.vnic_ocids.*...)[merge(local.nlb_instance_ocid.ocid.*...)[split("NAME:", var.ip_address)[1]][0]][0]][0] : null
  weight     = var.weight
}
