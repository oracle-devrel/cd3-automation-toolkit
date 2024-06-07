package terraform

import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan


#To enforce secure configuration for container engines
#default enforce_container_engine_config = false

enforce_container_engine_config {
    container := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    container.type == "oci_containerengine_cluster"

    container.is_private_cluster
    container.is_encryption_enabled
    container.is_pod_security_policy_enabled
}

#To enforce secure configuration for container instances
#default enforce_container_instance_config = false

enforce_container_instance_config {
    container := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    container.type == "oci_containerengine_node_pool"

    container.is_auto_scaling_enabled
    container.is_image_signature_verification_enabled
    container.is_kubernetes_dashboard_disabled
    container.is_node_public_access_disabled
}

#To enforce secure configuration for container clusters
#default enforce_container_cluster_config = false

enforce_container_cluster_config {
    cluster := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    cluster.type == "oci_containerengine_cluster"

    cluster.is_private_control_plane_enabled
    cluster.is_private_node_enabled
    cluster.is_kubernetes_dashboard_enabled
    cluster.is_calico_encryption_enabled
    #cluster.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_container_engine_config
     enforce_container_instance_config
     enforce_container_cluster_config

     allow := false
     msg := sprintf("%-10s: OCI container engine/instance/cluster Config is not alligned with CIS benchmarks",[allow])
}

