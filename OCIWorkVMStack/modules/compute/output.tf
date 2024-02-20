output "OCI_automation_VM_name" {
  description = "OCI automation VM name"
  value = data.oci_core_instance.instance.display_name
}
output "OCI_automation_VM_Private_IP" {
  description = "OCI automation VM's Private IP"
  value = data.oci_core_instance.instance.private_ip
}

output "OCI_automation_VM_Public_IP" {
  description = "OCI automation VM's Public IP"
  value = data.oci_core_instance.instance.public_ip
}