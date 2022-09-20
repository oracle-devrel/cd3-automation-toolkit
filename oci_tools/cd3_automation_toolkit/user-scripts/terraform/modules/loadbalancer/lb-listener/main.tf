// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Load Balancer
# Create Load Balancer Listener
############################

resource "oci_load_balancer_listener" "listener" {
  #Required
  default_backend_set_name = var.default_backend_set_name
  load_balancer_id         = var.load_balancer_id
  name                     = var.name
  port                     = var.port
  protocol                 = var.protocol

  #Optional
  dynamic "connection_configuration" {
    for_each = var.listeners[var.key_name].connection_configuration != [] ? var.listeners[var.key_name].connection_configuration : []
    content {
      #Required
      idle_timeout_in_seconds = connection_configuration.value.idle_timeout_in_seconds

      #Optional
      backend_tcp_proxy_protocol_version = var.protocol != "TCP" ? null : (connection_configuration.value.backend_tcp_proxy_protocol_version != "" ? connection_configuration.value.backend_tcp_proxy_protocol_version : 2)
    }
  }
  hostname_names      = var.hostname_names
  path_route_set_name = var.path_route_set_name
  routing_policy_name = var.routing_policy_name != "" ? var.routing_policy_name : null
  rule_set_names      = var.rule_set_names

  dynamic "ssl_configuration" {
    for_each = var.listeners[var.key_name].ssl_configuration != [] ? var.listeners[var.key_name].ssl_configuration : []
    content {

      #Optional
      certificate_name                  = var.certificate_name
      certificate_ids                   = ssl_configuration.value.certificate_ids
      cipher_suite_name                 = var.cipher_suite_name
      protocols                         = ssl_configuration.value.protocols != [] ? ssl_configuration.value.protocols : ["TLSv1.2"]
      server_order_preference           = ssl_configuration.value.server_order_preference           #TODO
      trusted_certificate_authority_ids = ssl_configuration.value.trusted_certificate_authority_ids #TODO
      verify_depth                      = ssl_configuration.value.verify_depth
      verify_peer_certificate           = ssl_configuration.value.verify_peer_certificate == null ? false : ssl_configuration.value.verify_peer_certificate
    }
  }
}
