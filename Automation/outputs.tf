/*
 * Copyright (c) 2023 Oracle and/or its affiliates. All rights reserved.
 */
output "OCI_automation_VM_name" {
  description = "OCI automation VM name"
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
output "OCI_automation_VM_Private_IP" {
  description = "OCI automation VM's Private IP"
  value = module.instance.OCI_automation_VM_Private_IP
}

output "OCI_automation_VM_Public_IP" {
  description = "OCI automation VM's Public IP"
  value = module.instance.OCI_automation_VM_Public_IP
}

output "automation_toolkit_setup_details" {
  value = <<EOT
     ------------------------------------------------------------------------------------------
     OCI Automation Toolkit Container setup log is present at /cd3user/mount_path/installToolkit.log. Check file for details.
     Container named as oci_toolkit has been created and
     /cd3user/mount_path directory from WorkVM Instance is mounted inside container as /cd3user/tenancies
     ------------------------------------------------------------------------------------------
     To verify podman image run command -
     sudo podman images
     ------------------------------------------------------------------------------------------
     To verify podman container run command -
     sudo podman ps -a
     ------------------------------------------------------------------------------------------
     To connect to container run command -
     sudo podman exec -it oci_toolkit bash
     ------------------------------------------------------------------------------------------
     EOT
}