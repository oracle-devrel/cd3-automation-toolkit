package terraform

#Enforce secure IAM resources for OCI.


import future.keywords.in
import input as tfplan

#default enforce_mfa = false
enforce_mfa {
    user := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    user.type == "oci_identity_user"
    user.is_mfa_enabled
    #user.defined_tags["cis.cis-benchmark"] == "true"
}


#To enforce secure access control for IAM users and groups
#default enforce_iam_access_control = false
enforce_iam_access_control {
    user := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    user.type == "oci_identity_user"

    user.is_mfa_activated
    user.is_api_keys_rotated
    user.is_password_policy_enforced
   # user.defined_tags["cis.cis-benchmark"] == "true"
}

#To enforce secure configuration for identity and access management (IAM) users
#default enforce_iam_user_config = false
enforce_iam_user_config {
    user := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    user.type == "oci_identity_user"

    user.is_mfa_enabled
    user.is_api_keys_disabled
    user.is_console_password_disabled
    #user.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_iam_access_control
     enforce_mfa
     enforce_iam_user_config
     allow := false

     msg := sprintf("%-10s: IAM resources are not alligned with CIS benchmarks",[allow])
}