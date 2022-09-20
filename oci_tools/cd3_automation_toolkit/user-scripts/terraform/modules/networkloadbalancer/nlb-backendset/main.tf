// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Backend Set
#######################################


resource "oci_network_load_balancer_backend_set" "backend_set" {
  #Required
  health_checker {
    #Required
    protocol = var.protocol

    #Optional
    interval_in_millis  = var.interval_in_millis
    port                = var.port
    response_body_regex = var.response_body_regex
    retries             = var.retries
    return_code         = var.return_code
    timeout_in_millis   = var.timeout_in_millis
    url_path            = var.url_path
  }
  name                     = var.name
  network_load_balancer_id = var.network_load_balancer_id
  policy                   = var.policy

  #Optional
  ip_version         = var.ip_version
  is_preserve_source = var.is_preserve_source
}

#terraform import "module.nlb-backend-sets[\"ash1-np-ade-bs\"].oci_network_load_balancer_backend_set.backend_set" networkLoadBalancers/ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma/backendSets/ash1-np-ade-bs