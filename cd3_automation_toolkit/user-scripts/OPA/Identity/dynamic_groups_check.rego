package terraform

#Ensure Dynamic groups are used for OCI instances, OCI Cloud databases and OCI functions to access
#OCI resources.
#TODO It has to be done through OCI CLI/Script and cant be done through terraform

import future.keywords.in
import input as tfplan

deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.type == "oci_identity_api_key"
     resource.change.actions[_] == "create"

     allow := false
     msg := sprintf("%-10s %-10q: Users are not allowed to upload/create API keys through terraform", [resource.address, allow])
}