# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall_policy_decryption_profile" "network_firewall_policy_decryption_profile" {
    #Required
    name = var.profile_name
    type = var.profile_type
    network_firewall_policy_id = var.network_firewall_policy_id
    are_certificate_extensions_restricted = var.are_certificate_extensions_restricted
    is_auto_include_alt_name = var.is_auto_include_alt_name
    is_expired_certificate_blocked = var.is_expired_certificate_blocked
    is_out_of_capacity_blocked =var.is_out_of_capacity_blocked
    is_revocation_status_timeout_blocked = var.is_revocation_status_timeout_blocked
    is_unknown_revocation_status_blocked = var.is_unknown_revocation_status_blocked
    is_unsupported_cipher_blocked = var.is_unsupported_cipher_blocked
    is_unsupported_version_blocked = var.is_unsupported_version_blocked
    is_untrusted_issuer_blocked = var.is_untrusted_issuer_blocked
}