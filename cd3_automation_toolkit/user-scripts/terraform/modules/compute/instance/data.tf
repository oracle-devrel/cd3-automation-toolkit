# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Data Block - Instance
## Create Instance and Boot Volume Backup Policy
#############################

locals {
  nsg_ids = var.nsg_ids != null ? flatten(tolist([for nsg in var.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)])) : null

  ADs = [
    for ad in data.oci_identity_availability_domains.ads.availability_domains : ad.name
  ]

  shapes_config = {
    for shape in data.oci_core_shapes.present_ad.shapes : shape.name => {
      memory_in_gbs = shape.memory_in_gbs
      ocpus         = shape.ocpus
    }
  }

  platform_configs = {
    for shape in data.oci_core_shapes.present_ad.shapes : shape.name => {
      config_type = length(shape.platform_config_options) > 0 ? element(flatten(shape.platform_config_options[*].type),0) : ""
    } if shape.name == var.shape
  }

  plugins_config        = var.plugins_details != null ? var.plugins_details : {}
  remote_execute_script = var.remote_execute == null ? "SCRIPT-NOT-SET" : var.remote_execute
  cloud_init_script     = var.cloud_init_script == null ? "SCRIPT-NOT-SET" : var.cloud_init_script
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_core_shapes" "present_ad" {
  compartment_id      = var.compartment_id
  availability_domain = var.availability_domain == "" || var.availability_domain == null ? element(local.ADs, 0) : var.availability_domain
}

data "oci_core_vcns" "oci_vcns_instances" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}
//
//data "oci_core_subnets" "oci_subnets_instances" {
//  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
//  display_name   = var.subnet_id
//  vcn_id         = data.oci_core_vcns.oci_vcns_instances[var.vcn_names[0]].virtual_networks.*.id[0]
//}

data "oci_core_dedicated_vm_hosts" "existing_vm_host" {
  count          = var.dedicated_vm_host_name != null ? 1 : 0
  compartment_id = var.compartment_id
  display_name   = var.dedicated_vm_host_name
  state          = "ACTIVE"
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each       = var.nsg_ids != null ? { for nsg in var.nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_instances[var.vcn_names[0]].virtual_networks.*.id[0]
}

#data "oci_core_boot_volumes" "all_boot_volumes" {
#  depends_on = [oci_core_instance.instance]
#  count     = var.boot_tf_policy != null ? 1 : 0
#  #Required
#  compartment_id = var.compartment_id
#  availability_domain =  var.availability_domain
#  filter {
#    name   = "display_name"
#    values = [join(" ", [var.display_name, "(Boot Volume)"])]
#  }
#  filter {
#    name = "state"
#    values = ["AVAILABLE"]
#  }
#}

data "oci_core_volume_backup_policies" "boot_vol_backup_policy" {
  count = var.boot_tf_policy != null ? 1 : 0

  filter {
    name   = "display_name"
    values = [lower(var.boot_tf_policy)]
  }
}

data "oci_core_volume_backup_policies" "boot_vol_custom_policy" {
  count          = var.boot_tf_policy != null ? 1 : 0
  compartment_id = local.policy_tf_compartment_id
  filter {
    name   = "display_name"
    values = [var.boot_tf_policy]
  }
}

################################
# Data Block - Instances
# Market Place Images
################################

data "oci_marketplace_listing_package_agreements" "listing_package_agreements" {
  count = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  #Required
  listing_id      = data.oci_marketplace_listing.listing.0.id
  package_version = data.oci_marketplace_listing.listing.0.default_package_version

  #Optional
  compartment_id = var.compartment_id
}

data "oci_marketplace_listing_package" "listing_package" {
  count = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  #Required
  listing_id      = data.oci_marketplace_listing.listing.0.id
  package_version = data.oci_marketplace_listing.listing.0.default_package_version

  #Optional
  compartment_id = var.compartment_id
}

data "oci_marketplace_listing_packages" "listing_packages" {
  count = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  #Required
  listing_id = data.oci_marketplace_listing.listing.0.id

  #Optional
  compartment_id = var.compartment_id
}

data "oci_marketplace_listings" "listings" {
  count             = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  name              = [var.source_image_id]
  #is_featured      = true  # Comment this line for GovCloud
  compartment_id    = var.compartment_id
}

data "oci_marketplace_listing" "listing" {
  count          = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  listing_id     = data.oci_marketplace_listings.listings.0.listings[0].id
  compartment_id = var.compartment_id
}

data "oci_core_app_catalog_listing_resource_versions" "app_catalog_listing_resource_versions" {
  count      = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  listing_id = data.oci_marketplace_listing_package.listing_package.0.app_catalog_listing_id
}

data "oci_core_app_catalog_listing_resource_version" "catalog_listing" {
  count            = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  listing_id       = data.oci_marketplace_listing_package.listing_package.0.app_catalog_listing_id
  resource_version = data.oci_marketplace_listing_package.listing_package.0.app_catalog_listing_resource_version
}

