package terraform

#Ensure API keys are not created for tenancy adminstrator users.
#TODO how to fetch the user is from tenany admin group since tf plan doesn't show that ?

import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan


deny[msg] {
     resource := tfplan.resource_changes[_]
     admins := data.administrators[_]
     resource.type == "oci_identity_api_key"
     resource.change.actions[_] == "create"
     deny := contains(resource.change.after.user_id,admins)


     msg := sprintf("%-10s %-10s: Tenancy admins are not allowed to upload/create API keys through terraform", [resource.address, deny])
}


