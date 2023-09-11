package terraform

import future.keywords.in
import input as tfplan

#enforce secure storage configuration
#Ensures that the storage configuration in OCI, specifically for block volumes, meets the required benchmarks for secure storage.

#default enforce_secure_storage_config = false
enforce_secure_storage_config {
    block_volume := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    block_volume.type == "oci_core_volume"

    block_volume.is_encryption_in_transit_enabled
    block_volume.is_encryption_at_rest_enabled
    block_volume.is_auto_tune_enabled
  #  block_volume.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_secure_storage_config
     allow := false

     msg := sprintf("%-10s: Secure storage configuration is not alligned with CIS benchmarks",[allow])
}