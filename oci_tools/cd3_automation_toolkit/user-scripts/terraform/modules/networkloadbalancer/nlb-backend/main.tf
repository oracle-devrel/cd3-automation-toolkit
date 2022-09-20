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
  ip_address = var.ip_address
  is_drain   = var.is_drain
  is_offline = var.is_offline
  name       = var.name
  target_id  = var.target_id
  weight     = var.weight
}

#terraform import "module.nlb-backends[\"ash1-adenp01a\"].oci_network_load_balancer_backend.backend" networkLoadBalancers/ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma/backendSets/ash1-np-ade-bs/backend/ash1-adenp01a
#terraform import "module.nlb-backends[\"ash1-adenp01a\"].oci_network_load_balancer_backend.backend" networkLoadBalancers/ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma/backendSets/ash1-np-ade-bs/backends/ocid1.privateip.oc1.iad.abuwcljrcwi75bfnlje6wqbr6vodykjbj2voahnunflpbkvuhlgffbdyjbda:5432
#terraform import "module.nlb-backends[\"ash1-adenp01c\"].oci_network_load_balancer_backend.backend" networkLoadBalancers/ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma/backendSets/ash1-np-ade-bs/backends/ash1-adenp01c
#terraform import "module.nlb-backends[\"ash1-adenp01b\"].oci_network_load_balancer_backend.backend" networkLoadBalancers/ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma/backendSets/ash1-np-ade-bs/backends/ash1-adenp01b
#oci nlb backend-set get --backend-set-name ash1-np-ade-bs --network-load-balancer-id ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma