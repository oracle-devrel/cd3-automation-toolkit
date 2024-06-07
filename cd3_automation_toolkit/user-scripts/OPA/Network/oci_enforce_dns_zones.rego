package terraform

import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan

#To enforce secure configuration for DNS zone

#default enforce_dns_zone_config = false
enforce_dns_zone_config {
    dnsZone := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    dnsZone.type == "oci_dns_zone"

    dnsZone.is_dns_zone_private
    dnsZone.is_dnssec_enabled
    dnsZone.is_dns_zone_forwarding_enabled
    dnsZone.is_dns_zone_query_logging_enabled
    dnsZone.is_dns_zone_query_logging_retention_enabled
    #dnsZone.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_dns_zone_config
     allow := false

     msg := sprintf("%-10s: DNZ Zone Config is not alligned with CIS benchmarks",[allow])
}
