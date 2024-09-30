/*
 * Copyright (c) 2023 Oracle and/or its affiliates. All rights reserved.
 */

module "compartment" {
  source = "./modules/compartment"
  count = var.instance_compartment_strategy == "Create New Compartment - Stack must be provisioned in home region" ? 1 : 0
  compartment_id    = var.parent_compartment_ocid
  compartment_name  = var.new_compartment_name
}

# Create VCN/network resources

module "network" {
  source = "./modules/network"
  vcn_compartment_ocid = local.vcn_compartment_ocid
  vcn_strategy         = var.vcn_strategy
  vcn_name             = var.vcn_name
  vcn_cidr             = var.vcn_cidr
  vcn_dns_label        = var.vcn_dns_label
  subnet_name          = var.subnet_name
  subnet_type          = var.subnet_type
  subnet_cidr          = var.subnet_cidr
  subnet_dns_label     = var.subnet_dns_label
  existing_drg_id      = var.existing_drg_id
  drg_attachment       = var.drg_attachment
  source_cidr          = var.source_cidr
}

module "instance" {
  source                    = "./modules/compute"
  vcn_strategy              = var.vcn_strategy == "Create New VCN" ? 1 : 0
  instance_image_ocid       = local.instance_image_ocid
  subnet_id                 = var.vcn_strategy == "Create New VCN" ? module.network.subnet_id : var.existing_subnet_id
  nsg_id                    = var.vcn_strategy == "Create New VCN" ? module.network.nsg_id : local.nsg_id
  instance_compartment_ocid = local.instance_compartment_ocid
  instance_name             = var.instance_name
  instance_shape            = var.instance_shape
  instance_ram              = var.instance_ram
  instance_ocpus            = var.instance_ocpus
  boot_volume_size          = var.boot_volume_size
  instance_ad               = var.instance_ad
  instance_fd               = var.instance_fd
  ssh_public_key            = var.ssh_public_key
  assign_public_ip          = local.assignPublicIP
  cloud_init_script         = var.cloud_init_script
  tenancy_ocid              = var.tenancy_ocid
  current_user_ocid         = var.current_user_ocid
  config_region             = var.region 
  tenancy_name              = local.tenancy_name
}

# This resource will wait for ~ 15 min to cloud init script to completed cd3 related steps
resource "time_sleep" "wait" {
  depends_on      = [module.instance]
  create_duration = "480s"

}
