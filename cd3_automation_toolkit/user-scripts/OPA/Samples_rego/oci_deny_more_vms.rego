#########################################################
# OCI VM deny rules for instance count, nsg's, public_ip#
#########################################################


package terraform

import future.keywords.in
import input as tfplan

# Deny if it creates more than 20VM's at one go in OCI.
deny_too_many_vms[deny] {
   
    instances := [res | res:=tfplan.resource_changes[_]; res.type == "oci_core_instance"]
    count(instances) > 20
    deny := true

}


# Deny if more than 5NSG's in VM.
deny[reason] {
    resource := tfplan.resource_changes[_]
   
    nsg_count := count(resource.change.after.create_vnic_details[_].nsg_ids)
    nsg_count > 5

    reason := sprintf(
        "%s: resource type %q is not allowed to have more than 5 nsg's",
        [resource.address, resource.type]
    )
}


# Deny if OCI instance has a public ip assigned.
deny[reject]{
  resource := tfplan.resource_changes[_]

  public_ip := resource.change.after.create_vnic_details[_].assign_public_ip

  public_ip == "true"

  reject := sprintf(
         "%s: resource type %q is not allowed to have public IP", 
	  [resource.address, resource.type]
	  )
}
