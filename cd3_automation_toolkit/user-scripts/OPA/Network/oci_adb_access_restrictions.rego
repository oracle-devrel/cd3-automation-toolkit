package terraform

###Ensure ADB access is restricted to allowed sources or deployed withing VCN.


import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan

deny_without_subnet_or_whitelist_ips {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_database_autonomous_database"
    resource.change.actions[_] in ["create", "update"]
    resource.change.subnet_id == null
}

deny_without_subnet_or_whitelist_ips {
    resource := tfplan.resource_changes[_]
    resource.type == "oci_database_autonomous_database"
    resource.change.actions[_] in ["create", "update"]
    resource.change.whitelisted_ips == null
}

deny[msg] {
     resource := tfplan.resource_changes[_]
     deny_without_subnet_or_whitelist_ips

     allow := false
     msg := sprintf("%-10s: CIS violation - ADB access should be inside VCN or allowed by whitelisted client IP's only", [allow])
}


