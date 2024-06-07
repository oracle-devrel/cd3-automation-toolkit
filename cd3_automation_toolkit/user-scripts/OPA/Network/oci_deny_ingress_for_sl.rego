package terraform

#Ensure no SL allow ingress from 0.0.0.0/0 to port 22 and 3389

import future.keywords.in
import input as tfplan


rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].source_port_range[_].min == 22
    resource.change.after.ingress_security_rules[_].tcp_options[_].source_port_range[_].max == 22
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].destination_port_range[_].min == 22
    resource.change.after.ingress_security_rules[_].tcp_options[_].destination_port_range[_].max == 22
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].min == 22
    resource.change.after.ingress_security_rules[_].tcp_options[_].max == 22
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].source_port_range[_].min == 3389
    resource.change.after.ingress_security_rules[_].tcp_options[_].source_port_range[_].max == 3389
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].destination_port_range[_].min == 3389
    resource.change.after.ingress_security_rules[_].tcp_options[_].destination_port_range[_].max == 3389
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].min == 3389
    resource.change.after.ingress_security_rules[_].tcp_options[_].max == 3389
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_].destination_port_range[_].min == 22
    resource.change.after.ingress_security_rules[_].tcp_options[_].destination_port_range[_].max == 22
}

rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_security_list"
    resource.mode == "managed"
    resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
    resource.change.after.ingress_security_rules[_].tcp_options[_]
}

deny[msg] {
     rules_validation_ingress
     allow := false

     msg := sprintf("%-10s: CIS violation - Security List CIDR ranges opened from internet for PORT 22/3389",[allow])
}
