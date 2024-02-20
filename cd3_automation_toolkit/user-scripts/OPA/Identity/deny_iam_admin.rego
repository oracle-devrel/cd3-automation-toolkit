package terraform

#Ensure IAM adminstrators cannot update tenancy Adminstrators group.
#TODO how to fetch the IAM admins and avoid updating tenancy adminstrators group ?

import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan


deny[msg] {
     resource := tfplan.resource_changes[_]
     iam_admins := data.IAM_Admins[_]
     admins := data.administrators[_]

     resource.type == "oci_identity_user_group_membership"
     resource.change.actions[_] in ["create", "update"]
     contains(resource.change.after.user_id, iam_admins)
     contains(resource.change.after.user_id, admins)

     allow := false
     msg := sprintf("%-10s %-10q: IAM Admins are not allowed to update Tenancy adminstrator(s) through terraform", [resource.address, allow])
}