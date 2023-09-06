package terraform

import future.keywords.in
import input as tfplan

#Ensure instances are deployed only inside a VCN.

deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.change.after.create_vnic_details[_].subnet_id != null

	 msg := sprintf(
         "%s: resource is not allowed to launch without VCN",
          [resource.address]
          )
}
