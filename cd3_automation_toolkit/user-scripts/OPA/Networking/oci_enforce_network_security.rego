package terraform

import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan

#To enforce secure network configuration for VCNs
#default enforce_vcn_network_config = false

enforce_vcn_network_config {
    vcn := tfplan.resource_changes[_]
    vcn.type == "oci_core_virtual_network"

    vcn.is_dns_private
    vcn.is_dns_public_access_restricted
    vcn.is_nat_gateway_disabled
    vcn.is_internet_gateway_disabled
   # vcn.defined_tags["cis.cis-benchmark"] == "true"
   msg = "VCN network configuration does not meet the required benchmarks."
}

#To enforce network security configuration
#default enforce_network_security_config = false

enforce_network_security_config {
    vcn := input.variables.tfplan.resource_changes[_].change.after
    vcn.type == "oci_core_virtual_network"

    vcn.is_dns_private
    vcn.is_dhcp_options_set
    vcn.is_security_list_default
    vcn.are_security_lists_stateless
    #vcn.defined_tags["cis.cis-benchmark"] == "true"
}

#To enforce secure network access configuration
#default enforce_network_access_config = false

enforce_network_access_config {
    security_list := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    security_list.type == "oci_core_security_list"

    security_list.ingress_security_rules[_].source.type == "CIDR_BLOCK"
    security_list.egress_security_rules[_].destination.type == "CIDR_BLOCK"
    #security_list.defined_tags["cis.cis-benchmark"] == "true"
}


#To enforce secure configuration for NAT gateways
#default enforce_nat_gateway_config = false
enforce_nat_gateway_config {
    natGateway := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    natGateway.type == "oci_core_nat_gateway"

    natGateway.is_private_ip_enabled
    natGateway.is_source_ip_verification_enabled
    natGateway.is_route_table_propagation_enabled
    natGateway.is_vcn_dns_resolution_enabled
    #natGateway.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_vcn_network_config
     enforce_network_security_config
     enforce_network_access_config
     enforce_nat_gateway_config

     allow := false
     msg := sprintf("%-10s: Network config is not alligned with CIS benchmarks",[allow])
}
