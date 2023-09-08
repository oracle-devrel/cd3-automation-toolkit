package terraform

#Ensure service level admins are created to manage resources of particular service.
#TODO Not doable through terraform i believe ? more inputs needed

import future.keywords.in
import input as tfplan

deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.type == "oci_identity_api_key"
     resource.change.actions[_] == "create"

     allow := false
     msg := sprintf("%-10s %-10q: Users are not allowed to upload/create API keys through terraform", [resource.address, allow])
}