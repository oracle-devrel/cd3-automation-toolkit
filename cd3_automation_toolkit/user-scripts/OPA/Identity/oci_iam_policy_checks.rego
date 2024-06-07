package terraform

#To enforce secure configuration for identity and access management (IAM) policies
#This policy ensures that the configuration for identity and access management (IAM) policies in OCI meets the required benchmarks

import future.keywords.in
import input as tfplan

#default enforce_iam_policy_config = false

enforce_iam_policy_config {
    policy := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    policy.type == "oci_identity_policy"

    policy.is_compartments_restricted
    policy.is_network_sources_restricted
    policy.is_policy_versioning_enabled
    policy.is_iam_password_policy_enabled
    #policy.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_iam_policy_config
     allow := false

     msg := sprintf("%-10s: IAM secure configurations are not alligned with CIS benchmarks",[allow])
}