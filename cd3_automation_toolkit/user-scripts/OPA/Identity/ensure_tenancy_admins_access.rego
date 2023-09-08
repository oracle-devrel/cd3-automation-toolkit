package terraform

#Ensure permissions on all resources are given only to the tenancy adminstrator group.
#TODO Not doable/needed through terraform i believe ? more inputs required

import future.keywords.in
import input as tfplan

deny[msg] {
     resource := tfplan.resource_changes[_]
     resource.type == "oci_identity_api_key"
     resource.change.actions[_] == "create"

     allow := false
     msg := sprintf("%-10s %-10q: Users are not allowed to upload/create API keys through terraform", [resource.address, allow])
}