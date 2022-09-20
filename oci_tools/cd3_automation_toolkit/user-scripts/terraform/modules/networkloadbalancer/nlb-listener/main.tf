// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Listener
#######################################

resource "oci_network_load_balancer_listener" "listener" {
  #Required
  default_backend_set_name = var.default_backend_set_name
  name                     = var.name
  network_load_balancer_id = var.network_load_balancer_id
  port                     = var.port
  protocol                 = var.protocol

  #Optional
  ip_version = var.ip_version
}

#terraform import "module.nlb-listeners[\"ash1-np-ade-lsnr\"].oci_network_load_balancer_listener.listener" networkLoadBalancers/ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma/listeners/ash1-np-ade-lsnr