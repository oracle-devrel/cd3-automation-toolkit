package terraform
import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan

#To enforce secure logging and monitoring configuration
#This policy applies to resources such as logging configurations, log groups, and monitoring alarms.
#If all conditions are met for any logging or monitoring resource, the enforce_logging_monitoring_config variable will be set to true, indicating compliance with the policy


#default enforce_logging_monitoring_config = false
enforce_logging_monitoring_config {
    logging_monitoring := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    logging_monitoring.type == "oci_logging_log_analytics_config" ||
    logging_monitoring.type == "oci_logging_log_group" ||
    logging_monitoring.type == "oci_monitoring_alarm"

    logging_monitoring.is_logging_enabled
    logging_monitoring.is_monitoring_enabled
    logging.is_log_retention_enabled
    logging.is_log_export_enabled
    #logging_monitoring.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_logging_monitoring_config
     allow := false

     msg := sprintf("%-10s: Logging/monitoring Config is not alligned with CIS benchmarks",[allow])
}