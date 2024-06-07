locals {
  instance_compartment_ocid = var.instance_compartment_strategy == "Create New Compartment - Stack must be provisioned in home region" ? module.compartment[0].compartment_tf_id : var.instance_compartment_ocid
  #vcn_compartment_ocid = var.vcn_strategy == "Use Existing VCN" ? var.vcn_compartment_ocid : module.compartment[0].compartment_tf_id
  vcn_compartment_ocid = var.vcn_strategy == "Use Existing VCN" ? var.vcn_compartment_ocid : local.instance_compartment_ocid
  nsg_id         = var.assign_existing_nsg == true ? var.existing_nsg_id : null
  is_public_sub  = var.vcn_strategy == "Use Existing VCN" ? !data.oci_core_subnet.subnet[0].prohibit_public_ip_on_vnic : false
  assignPublicIP = var.vcn_strategy == "Create New VCN" ? var.assign_public_ip : ((local.is_public_sub && var.assign_publicip_existing_subnet) == true ? true : false)
  tenancy_name   = data.oci_identity_tenancy.tenancy.name

  # Logic to select Oracle Autonomous Linux 7 platform image (version pegged in data source filter)
  #platform_image_id = data.oci_core_images.ol7.images[0].id
  # Logic to choose a custom image or a marketplace image.
  #compute_image_id = var.mp_subscription_enabled ? var.mp_listing_resource_id : var.instance_image_ocid
  # Local to control subscription to Marketplace image.
  mp_subscription_enabled = var.mp_subscription_enabled ? 1 : 0

  # Marketplace Image listing variables - required for subscription only
  listing_id               = var.mp_listing_id
  listing_resource_id      = var.mp_listing_resource_id
  listing_resource_version = var.mp_listing_resource_version

  os_version = var.instance_os_version == "Oracle-Linux-9" ? 9 : (var.instance_os_version == "Oracle-Linux-8" ? 8 : 7.9)

  instance_image_ocid = data.oci_core_images.oracle_linux.images[1].id

}
