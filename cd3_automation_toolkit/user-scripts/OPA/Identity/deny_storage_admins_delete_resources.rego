package terraform

#Ensure storage service-level admins cannot delete resources they manage.
#TODO fetch storage level admins if exists and match against the resource user names before deny.

import future.keywords.in
import input as tfplan

storage_admin_group = ["storage_admins"]

deny[msg] {
     resource := tfplan.resource_changes[_]
     storage_admins := data.storage_admins[_]
     resource.type == "oci_core_volume"
     resource.change.actions[_] == "delete"

     allow := false
     msg := sprintf("%-10s %-10q: Storage admins are not allowed to delete resources through terraform", [resource.address, allow])
}