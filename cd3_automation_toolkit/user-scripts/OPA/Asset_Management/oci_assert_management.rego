package terraform

#Ensure atleast one compartment to deploy cloud resources in the tenancy.
#Ensure NO resources are created in the ROOT compartment


import future.keywords.in
import input as tfplan

tenancy_id := "<TENANCY_OCID TO BE PLACED HERE>"


deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.change.actions[_] in ["create", "update"]
     resource.change.after.compartment_id == tenancy_id
     allow := false
     msg := sprintf("%10s %-10s: Users are NOT allowed to create resources in the ROOT compartment", [resource.address, allow])
}