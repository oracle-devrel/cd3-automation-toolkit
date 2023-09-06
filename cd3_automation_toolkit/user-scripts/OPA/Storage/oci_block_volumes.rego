package terraform

#Ensure BV's are encrypted with CMK
#Ensure Boot Volumes are encrypted with CMK

import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan


deny_volume {
     resource := tfplan.resource_changes[_]
     resource.mode == "managed"
     resource.type == "oci_core_volume"
     resource.change.actions[_] in ["create", "update"]
     resource.change.after.kms_key_id == null

     msg := sprintf("%-10q: Block volumes need to be encrypted with CMK through terraform as per CIS", [resource.address])
}

deny_volume {
     resource := tfplan.resource_changes[_]
     resource.mode == "managed"
     resource.type == "oci_core_boot_volume"
     resource.change.actions[_] in ["create", "update"]
     resource.change.after.kms_key_id == null

     msg := sprintf("%-10q: Boot volumes need to be encrypted with CMK through terraform as per CIS", [resource.address])
}

deny[msg] {
    deny_volume
    allow := false

    msg := sprintf("%-10s: Boot/Block Volumes need to be encrypted with CMK for terraform as per CIS standard's", [allow])

}


#To enforce secure configuration for block volumes
default enforce_block_volume_config = false

enforce_block_volume_config {
    volume := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    volume.type == "oci_core_volume"

    volume.is_encryption_in_transit_enabled
    volume.is_volume_backup_enabled
    volume.is_volume_group_backup_enabled
    volume.is_volume_performance_reporting_enabled
    #volume.defined_tags["cis.cis-benchmark"] == "true"
}