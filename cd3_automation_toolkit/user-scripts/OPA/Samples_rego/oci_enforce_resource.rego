##################################
# OCI allowed terraform resources#
##################################


package terraform

import input as tfplan

# Allowed Terraform resources
allowed_resources = [
  "oci_core_instance",
  "oci_core_boot_volume",
  "oci_core_drg",
  "oci_core_nat_gateway",
  "oci_core_remote_peering_connection",
  "oci_core_vcn",
  "oci_core_volume_attachment",
  "oci_core_vnic_attachment",
  "oci_core_volume_group",
  "oci_core_public_ip",
  "oci_container_engine_cluster",
  "oci_container_engine_node_pool",
  "oci_container_engine_virtual_node_pool",
  "oci_core_network_security_group",
  "oci_core_network_security_group_security_rule",
  "oci_core_security_list",
  "oci_dns_zone",
  "oci_dns_record",
  "oci_dns_resolver",
  "oci_dns_view",
  "oci_dns_resolver",
  "oci_load_balancer_backend",
  "oci_load_balancer_backend_set",
  "oci_load_balancer_listener",
  "oci_load_balancer_load_balancer",
  "oci_load_balancer_path_route_set",
  "oci_load_balancer_certificate",
  "oci_database_autonomous_container_database_dataguard_association",
  "oci_database_autonomous_container_database",
  "oci_database_autonomous_exadata_infrastructure",
  "oci_database_cloud_autonomous_vm_cluster",
  "oci_database_cloud_vm_cluster",
  "oci_database_database",
  "oci_identity_user_capabilities_management",
  "oci_identity_tag_namespace",
  "oci_file_storage_file_system",
  "oci_file_storage_mount_target",
  "oci_file_storage_export",
  "oci_kms_key",
  "oci_kms_vault",
  "oci_kms_encrypted_data",
  "oci_cloud_guard_cloud_guard_configuration"
]


array_contains(arr, elem) {
  arr[_] = elem
}

deny[reason] {
    resource := tfplan.resource_changes[_]
    action := resource.change.actions[count(resource.change.actions) - 1]
    array_contains(["create", "update"], action)  # allow destroy action

    not array_contains(allowed_resources, resource.type)

    reason := sprintf(
        "%s: resource type %q is not allowed in tenancy",
        [resource.address, resource.type]
    )
}
