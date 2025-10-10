package terraform

#Ensure no NSG allow ingress from 0.0.0.0/0 to port 22 and 3389
import future.keywords.in
import input as tfplan


nsg_rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_network_security_group_security_rule"
    resource.mode == "managed"
    resource.change.actions[_] in ["create", "update"]
    resource.change.after.direction == "INGRESS"
    resource.change.after.source == "0.0.0.0/0"
    resource.change.after.tcp_options[_].source_port_range[_].min == 22
    resource.change.after.tcp_options[_].source_port_range[_].max == 22
}

nsg_rules_validation_ingress {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_core_network_security_group_security_rule"
    resource.mode == "managed"
    resource.change.actions[_] in ["create", "update"]
    resource.change.after.direction == "INGRESS"
    resource.change.after.source == "0.0.0.0/0"
    resource.change.after.tcp_options[_].source_port_range[_].min == 3389
    resource.change.after.tcp_options[_].source_port_range[_].max == 3389
}

deny[msg] {
     nsg_rules_validation_ingress
     allow := false

     msg := sprintf("%-10s: CIS violation - OCI NSG should not have open CIDR ranges from internet for PORT 22/3389",[allow])
}
