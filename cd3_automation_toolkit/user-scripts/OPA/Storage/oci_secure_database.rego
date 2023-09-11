package terraform

import future.keywords.in
import input as tfplan

#To ensures the backup and recovery configuration in OCI, specifically for databases, meets the required benchmarks

#default enforce_backup_recovery_config = false
enforce_backup_recovery_config {
    database := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    database.type == "oci_database_database"

    database.is_backup_enabled
    database.is_data_guard_enabled
    database.is_recovery_window_valid
    database.is_point_in_time_recovery_enabled
   # database.defined_tags["cis.cis-benchmark"] == "true"
}

#To enforce secure configuration for database instances

#default enforce_database_instance_config = false
enforce_database_instance_config {
    database := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    database.type == "oci_database_db_system"

    database.is_tde_enabled
    database.is_ssl_enabled
    database.is_data_guard_enabled
    database.is_auto_backup_enabled
   # database.defined_tags["cis.cis-benchmark"] == "true"
}

#Policy to enforce the use of encryption for data in transit:
#default enforce_data_in_transit_encryption = false
enforce_data_in_transit_encryption {
    resource_type := input.planned_values.root_module.child_modules[_].resources[_].type
    resource := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes

    resource_type == "oci_autonomous_database"
    resource.is_ssl_enabled
}

deny[msg] {
     enforce_backup_recovery_config
     enforce_database_instance_config
     enforce_data_in_transit_encryption
     allow := false

     msg := sprintf("%-10s: Database configurations is not alligned with CIS benchmarks",[allow])
}