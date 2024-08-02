# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Backend Set
#######################################


resource "oci_network_load_balancer_backend_set" "backend_set" {
  #Required
  health_checker {
    #Required
    protocol = var.protocol
    dynamic "dns" {
    for_each = var.domain_name != null ? {1:1} : {}
    content {
            #Required
            domain_name = var.domain_name
            #Optional
            query_class = var.query_class
            query_type = var.query_type
            rcodes = var.rcodes
            transport_protocol = var.transport_protocol
        }
    }
    #Optional
    interval_in_millis  = var.interval_in_millis
    port                = var.port
    request_data        = var.request_data
    response_body_regex = var.response_body_regex
    response_data       = var.response_data
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
  is_instant_failover_enabled = var.is_instant_failover_enabled
  is_preserve_source = var.is_preserve_source
  is_fail_open       = var.is_fail_open
}
