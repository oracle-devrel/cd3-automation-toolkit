/*
 * Copyright (c) 2023 Oracle and/or its affiliates. All rights reserved.
 */
output "CD3_Automation_VM_Name" {
  description = "CD3 Automation Toolkit WorkVM Name"
  value = module.instance.OCI_automation_VM_name
}

output "OCI_compartment_name" {
  description = "Compartment name"
  value = data.oci_identity_compartment.compartment.name
}
output "OCI_compartment_id" {
  description = "Compartment ocid"
  value = data.oci_identity_compartment.compartment.id
}
output "CD3_Automation_VM_Private_IP" {
  description = "CD3 Automation Toolkit WorkVM's Private IP"
  value = module.instance.OCI_automation_VM_Private_IP
}

output "CD3_Automation_VM_Public_IP" {
  description = "CD3 Automation Toolkit WorkVM's Public IP"
  value = module.instance.OCI_automation_VM_Public_IP
}

output "automation_toolkit_setup_details" {
  value = <<EOT
     ------------------------------------------------------------------------------------------
     CD3 Automation Toolkit Container setup log is present at /cd3user/mount_path/installToolkit.log. Check file for details.
     Container named as cd3_toolkit has been created and
     /cd3user/mount_path directory from WorkVM Instance is mounted inside container as /cd3user/tenancies
     ------------------------------------------------------------------------------------------
     To verify podman image run command -
     sudo podman images
     ------------------------------------------------------------------------------------------
     To verify podman container run command -
     sudo podman ps -a
     ------------------------------------------------------------------------------------------
     To connect to container run command -
     sudo podman exec -it cd3_toolkit bash
     ------------------------------------------------------------------------------------------
     EOT
}