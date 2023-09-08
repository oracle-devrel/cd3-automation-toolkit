package terraform
import future.keywords.in
import future.keywords.if
import future.keywords.contains
import input as tfplan



#To enforce SSL/TLS configuration for load balancers
#default enforce_load_balancer_ssl_config = false

enforce_load_balancer_ssl_config {
    lb := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    lb.type == "oci_load_balancer_load_balancer"

    lb.is_ssl_configuration_enabled
    lb.is_ssl_cipher_suite_strong
    #lb.defined_tags["cis.cis-benchmark"] == "true"
}

#To enforce secure configuration for load balancers
#default enforce_load_balancer_config = false

enforce_load_balancer_config {
    lb := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    lb.type == "oci_load_balancer_load_balancer"

    lb.is_https_enabled
    lb.is_http_to_https_redirection_enabled
    lb.is_backend_ssl_enabled
    lb.is_listener_ssl_enabled
    lb.is_backend_set_private
    lb.is_health_check_enabled
    lb.is_backend_set_encryption_enabled
    lb.is_ssl_cipher_suite_preferred
    lb.is_listener_encryption_enabled
    lb.is_backend_logging_enable
    #lb.defined_tags["cis.cis-benchmark"] == "true"
}


deny[msg] {
     enforce_load_balancer_ssl_config
     enforce_load_balancer_config

     allow := false
     msg := sprintf("%-10s: Load Balancer Config is not alligned with CIS benchmarks",[allow])
}
