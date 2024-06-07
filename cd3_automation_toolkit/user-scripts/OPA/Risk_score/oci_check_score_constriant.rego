package terraform.oci
import input as tfplan


 # acceptable score-policy for automated authorization
 blast_radius := 50

 # weights assigned for each operation on each resource-type
 #weights := params.weights
 weights := {
  "oci_core_instance": {"delete": 5 , "create": 2, "modify": 1},
  "oci_core_boot_volume": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_drg": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_nat_gateway": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_remote_peering_connection": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_vcn": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_volume_attachment": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_vnic_attachment": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_volume_group": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_public_ip": {"delete": 5, "create": 2, "modify": 1},
  "oci_container_engine_cluster": {"delete": 5, "create": 2, "modify": 1},
  "oci_container_engine_node_pool": {"delete": 5, "create": 2, "modify": 1},
  "oci_container_engine_virtual_node_pool": {"delete": 5, "create": 2, "modify": 1},
  "oci_dns_zone": {"delete": 5, "create": 2, "modify": 1},
  "oci_dns_record":  {"delete": 5, "create": 2, "modify": 1},
  "oci_dns_resolver":  {"delete": 5, "create": 2, "modify": 1},
  "oci_dns_view":  {"delete": 5, "create": 2, "modify": 1},
  "oci_dns_resolver":  {"delete": 5, "create": 2, "modify": 1},
  "oci_core_security_list": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_network_security_group": {"delete": 5, "create": 2, "modify": 1},
  "oci_core_network_security_group_security_rule": {"delete": 5, "create": 1, "modify": 1},
  "oci_load_balancer_backend":  {"delete": 5, "create": 2, "modify": 1},
  "oci_load_balancer_backend_set":  {"delete": 5, "create": 2, "modify": 1},
  "oci_load_balancer_listener":  {"delete": 5, "create": 2, "modify": 1},
  "oci_load_balancer_load_balancer":  {"delete": 5, "create": 2, "modify": 1},
  "oci_load_balancer_path_route_set":  {"delete": 5, "create": 2, "modify": 1},
  "oci_load_balancer_certificate":  {"delete": 5, "create": 2, "modify": 1},
  "oci_database_autonomous_container_database_dataguard_association":  {"delete": 5, "create": 2, "modify": 1},
  "oci_database_autonomous_container_database":  {"delete": 2, "create": 2, "modify": 1},
  "oci_database_autonomous_exadata_infrastructure":  {"delete": 5, "create": 2, "modify": 1},
  "oci_database_cloud_autonomous_vm_cluster": {"delete": 5, "create": 2, "modify": 1},
  "oci_database_cloud_vm_cluster": {"delete": 5, "create": 2, "modify": 1},
  "oci_database_database": {"delete": 5, "create": 2, "modify": 1},
  "oci_identity_policies": {"delete": 5, "create": 2, "modify": 1},
  "oci_identity_user_capabilities_management": {"delete": 5, "create": 2, "modify": 1},
  "oci_identity_tag_namespace": {"delete": 5, "create": 2, "modify": 1},
  "oci_file_storage_file_system": {"delete": 5, "create": 2, "modify": 1},
  "oci_file_storage_mount_target": {"delete": 5, "create": 2, "modify": 1},
  "oci_file_storage_export": {"delete": 5, "create": 2, "modify": 1},
  "oci_kms_key": {"delete": 5, "create": 2, "modify": 1 },
  "oci_kms_vault": {"delete": 5, "create": 2, "modify": 1 },
  "oci_kms_encrypted_data": {"delete": 5, "create": 2, "modify": 1 },
  "oci_cloud_guard_cloud_guard_configuration": {"delete": 5, "create": 2, "modify": 1 }
 }

 # Consider exactly these resource types in calculations
 resource_types := {"oci_core_instance",
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
  "oci_cloud_guard_cloud_guard_configuration"}

# Compute the score-policy for a Terraform plan as the weighted sum of deletions, creations, modifications
score := s {
 all := [x |
  some resource_type
  crud := weights[resource_type]
  del := crud.delete * num_deletes[resource_type]
  new := crud.create * num_creates[resource_type]
  mod := crud.modify * num_modifies[resource_type]
  x := (del + new) + mod
 ]

 s := sum(all)
}


#Whether there is any change to IAM policies
touches_iam {
 all := resources.oci_identity_policies
 count(all) > 0
}

####################
# Terraform Library
####################

# list of all resources of a given type
resources[resource_type] := all {
 some resource_type
 resource_types[resource_type]
 all := [name |
  name := tfplan.resource_changes[_]
  name.type == resource_type
 ]
}

# number of creations of resources of a given type
num_creates[resource_type] := num {
 some resource_type
 resource_types[resource_type]
 all := resources[resource_type]
 creates := [res | res := all[_]; res.change.actions[_] == "create"]
 num := count(creates)
}

# number of deletions of resources of a given type
num_deletes[resource_type] := num {
 some resource_type
 resource_types[resource_type]
 all := resources[resource_type]
 deletions := [res | res := all[_]; res.change.actions[_] == "delete"]
 num := count(deletions)
}

# number of modifications to resources of a given type
num_modifies[resource_type] := num {
 some resource_type
 resource_types[resource_type]
 all := resources[resource_type]
 modifies := [res | res := all[_]; res.change.actions[_] == "update"]
 num := count(modifies)
}