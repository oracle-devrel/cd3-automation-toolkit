package terraform

#To enforce secure access to virtual machines:
#default enforce_vm_access_config = false
enforce_vm_access_config {
    vm := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    vm.type == "oci_core_instance"

    vm.are_ssh_passwords_disabled
    vm.is_ssh_key_required
   # vm.defined_tags["cis.cis-benchmark"] == "true"
}

#To enforce secure configuration for virtual machine instances
#default enforce_vm_instance_config = false
enforce_vm_instance_config {
    vm := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    vm.type == "oci_core_instance"

    vm.is_ssh_password_auth_disabled
    vm.is_agent_config_disabled
    vm.is_public_ip_disabled
    vm.is_cloud_init_disabled
    #vm.defined_tags["cis.cis-benchmark"] == "true"
}

deny[msg] {
     enforce_vm_access_config
     enforce_vm_instance_config
     allow := false

     msg := sprintf("%-10s: Secure access/secure configurations for VMs are not alligned with CIS benchmarks",[allow])
}