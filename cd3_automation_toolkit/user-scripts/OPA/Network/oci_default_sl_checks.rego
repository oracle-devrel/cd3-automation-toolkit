package terraform

#Ensure default SL of VCN allows only ICMP and restricts all other traffic.

import future.keywords.in
import input as tfplan


deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.type == "oci_core_default_security_list"
     resource.mode == "managed"
     #resource.change.after.ingress_security_rules[_].source == "0.0.0.0/0"
     not resource.change.after.protocol == "ICMP"
     allow := false

     msg := sprintf(
      "%s: Ensure default SL of VCN allows only ICMP and restricts all other traffic %q",
      [resource.address, allow ]
      )
}