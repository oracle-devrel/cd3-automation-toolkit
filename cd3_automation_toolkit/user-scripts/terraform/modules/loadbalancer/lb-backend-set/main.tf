# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Load Balancer
# Create Load Balancer Backend Set
############################

resource "oci_load_balancer_backend_set" "backend_set" {
  #Required
  health_checker {
    #Required
    protocol = var.protocol

    #Optional
    interval_ms         = var.interval_ms
    is_force_plain_text = var.is_force_plain_text
    port                = var.port
    response_body_regex = var.response_body_regex
    retries             = var.retries
    return_code         = var.return_code
    timeout_in_millis   = var.timeout_in_millis
    url_path            = var.url_path
  }
  load_balancer_id = var.load_balancer_id
  name             = var.name
  policy           = var.policy

  #Optional
  dynamic "lb_cookie_session_persistence_configuration" {
    for_each = var.backend_sets[var.key_name].lb_cookie_session != null ? var.backend_sets[var.key_name].lb_cookie_session : []

    #Optional
    content {
      cookie_name        = lb_cookie_session_persistence_configuration.value.cookie_name
      disable_fallback   = lb_cookie_session_persistence_configuration.value.disable_fallback
      domain             = lb_cookie_session_persistence_configuration.value.domain
      is_http_only       = lb_cookie_session_persistence_configuration.value.is_http_only
      is_secure          = lb_cookie_session_persistence_configuration.value.is_secure
      max_age_in_seconds = lb_cookie_session_persistence_configuration.value.max_age_in_seconds
      path               = lb_cookie_session_persistence_configuration.value.path
    }
  }
  dynamic "session_persistence_configuration" {
    for_each = var.backend_sets[var.key_name].session_persistence_configuration != null ? var.backend_sets[var.key_name].session_persistence_configuration : []

    content {
      #Required
      cookie_name = session_persistence_configuration.value.cookie_name

      #Optional
      disable_fallback = session_persistence_configuration.value.disable_fallback == null ? "false" : session_persistence_configuration.value.disable_fallback
    }
  }
  dynamic "ssl_configuration" {
    for_each = var.backend_sets[var.key_name].ssl_configuration != null ? var.backend_sets[var.key_name].ssl_configuration : []

    content {
      #Optional
      certificate_ids                   = ssl_configuration.value.certificate_ids
      certificate_name                  = var.certificate_name
      cipher_suite_name                 = var.cipher_suite_name
      protocols                         = ssl_configuration.value.protocols
      server_order_preference           = ssl_configuration.value.server_order_preference           #TODO
      trusted_certificate_authority_ids = ssl_configuration.value.trusted_certificate_authority_ids #TODO
      verify_depth                      = ssl_configuration.value.verify_depth
      verify_peer_certificate           = ssl_configuration.value.verify_peer_certificate
    }
  }
}