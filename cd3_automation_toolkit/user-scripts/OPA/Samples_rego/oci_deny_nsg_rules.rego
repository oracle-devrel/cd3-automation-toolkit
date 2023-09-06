#######################################
# Deny NSG rules with open CIDR ranges#
#######################################


package terraform

import future.keywords.in
import input as tfplan



deny_nsg_rules[msg] {
     resource := tfplan.resource_changes[_]
     resource.type == "oci_core_network_security_group_security_rule"
     resource.mode == "managed"
     resource.change.after.direction == "INGRESS"
    
     resource.change.after.source == "0.0.0.0/0"
     deny := true

     msg := sprintf(
      "%s: CIS Violation - resource should not have open INGRESS CIDR ranges from internet %q",
      [resource.address, "0.0.0.0/0"]
      )

}
