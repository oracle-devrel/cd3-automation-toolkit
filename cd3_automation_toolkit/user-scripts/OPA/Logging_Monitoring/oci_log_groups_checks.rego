package terraform

import future.keywords.in
import input as tfplan

#Policy to enforce logging and monitoring configuration:

#default enforce_logging_monitoring = false
enforce_logging_monitoring {
    log_group := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    log_group.type == "oci_logging_log_group"

    log_group.is_logs_to_object_storage_enabled
    log_group.is_logs_to_cloud_insight_enabled
    log_group.is_logs_to_event_service_enabled
    log_group.is_retention_enabled
    #log_group.defined_tags["cis.cis-benchmark"] == "true"
}


deny[msg] {
     enforce_logging_monitoring
     allow := false

     msg := sprintf("%-10s: Log-group config is not alligned with CIS benchmarks",[allow])
}