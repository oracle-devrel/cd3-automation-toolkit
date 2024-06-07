package terraform

#Ensure OCI iam user accounts have a valid and current email address.


import future.keywords.in
import input as tfplan

deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.type == "oci_identity_user"
     resource.change.actions[_] == "create"
     resource.change.after.email == null

     allow := false
     msg := sprintf("%-10s %-10q: Ensure OCI iam user accounts have a valid and current email address", [resource.address, allow])
}