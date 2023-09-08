package terraform

#This Rego policy calculates a risk score for detecting IAM policy changes in Oracle Cloud Infrastructure (OCI).
#It assigns a risk score of 10.0 if there are IAM policy changes that include at least one "DENY" statement, indicating a high-risk level for policy modifications

default risk_score = 0.0

risk_score = 5.0 {
    resource_type := input.planned_values.root_module.child_modules[_].resources[_].type
    resource_type == "oci_identity_policy"
    count(input.planned_values.root_module.child_modules[_].resources[_].instances) > 0
}

risk_score = 8.0 {
    resource_type := input.planned_values.root_module.child_modules[_].resources[_].type
    resource_type == "oci_identity_policy"
    resource := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    resource.lifecycle != "delete"
    resource.permission_changes[_].permission_action == "ALLOW"
    resource.permission_changes[_].permission != "READ"
}

risk_score = 10.0 {
    resource_type := input.planned_values.root_module.child_modules[_].resources[_].type
    resource_type == "oci_identity_policy"
    resource := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    resource.lifecycle != "delete"
    has_denied_changes := count(resource.permission_changes) > 0 {
        permission_changes[_].permission_action == "DENY"
    }
    has_denied_changes
}

risk_score = 0.0 {
    not risk_score[_]
}