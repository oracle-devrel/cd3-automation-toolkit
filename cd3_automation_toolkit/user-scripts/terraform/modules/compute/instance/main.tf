// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Resource Block - Instance
## Create Instance and Boot Volume Backup Policy
#############################

resource "oci_core_instance" "instance" {
  #Required
  availability_domain                 = var.availability_domain
  compartment_id                      = var.compartment_id
  capacity_reservation_id             = var.capacity_reservation_id
  shape                               = var.shape
  dedicated_vm_host_id                = var.dedicated_vm_host_name != null ? data.oci_core_dedicated_vm_hosts.existing_vm_host[0].dedicated_vm_hosts[0]["id"] : null
  defined_tags                        = var.defined_tags
  display_name                        = var.display_name
  extended_metadata                   = var.extended_metadata
  fault_domain                        = var.fault_domain
  freeform_tags                       = var.freeform_tags
  ipxe_script                         = var.ipxe_script
  is_pv_encryption_in_transit_enabled = var.create_is_pv_encryption_in_transit_enabled
  metadata = {
    ssh_authorized_keys = var.ssh_public_keys
  }
  preserve_boot_volume = var.preserve_boot_volume

  dynamic "preemptible_instance_config" {
    for_each = var.preemptible_instance_config
    content {
      #Required
      preemption_action {
        #Required
        type = preemptible_instance_config.value["action_type"]
        #Optional
        preserve_boot_volume = preemptible_instance_config.value["preserve_boot_volume"]
      }
    }
  }

  #Optional
  agent_config {
    #Optional
    are_all_plugins_disabled = var.all_plugins_disabled
    is_management_disabled   = var.is_management_disabled
    is_monitoring_disabled   = var.is_monitoring_disabled

    dynamic "plugins_config" {
      #Required
      for_each = var.plugins_details
      content {
        desired_state = plugins_config.value["desired_state"]
        name          = plugins_config.value["name"]
      }
    }
  }
  availability_config {
    #Optional
    is_live_migration_preferred = var.is_live_migration_preferred
    recovery_action             = var.recovery_action
  }

  create_vnic_details {
    #Optional
    assign_private_dns_record = var.assign_private_dns_record
    assign_public_ip          = var.assign_public_ip
    defined_tags              = var.vnic_defined_tags != {} ? var.vnic_defined_tags : var.defined_tags
    display_name              = var.vnic_display_name != "" && var.vnic_display_name != null ? var.vnic_display_name : var.display_name
    freeform_tags             = var.vnic_freeform_tags != {} ? var.vnic_freeform_tags : var.freeform_tags
    hostname_label            = var.hostname_label
    nsg_ids                   = var.nsg_ids != null ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : null
    private_ip                = var.private_ip
    subnet_id                 = var.subnet_id
    vlan_id                   = var.vlan_id
    skip_source_dest_check    = var.skip_source_dest_check
  }

  instance_options {
    #Optional
    are_legacy_imds_endpoints_disabled = var.are_legacy_imds_endpoints_disabled
  }

  launch_options {
    #Optional
    boot_volume_type                    = var.boot_volume_type
    firmware                            = var.firmware
    is_consistent_volume_naming_enabled = var.is_consistent_volume_naming_enabled
    is_pv_encryption_in_transit_enabled = var.update_is_pv_encryption_in_transit_enabled
    network_type                        = var.network_type
    remote_data_volume_type             = var.remote_data_volume_type
  }

  dynamic "platform_config" {
    for_each = var.platform_config
    content {
      #Required
      type = platform_config.value["config_type"]
      #Optional
      is_measured_boot_enabled           = platform_config.value["is_measured_boot_enabled"]
      is_secure_boot_enabled             = platform_config.value["is_secure_boot_enabled"]
      is_trusted_platform_module_enabled = platform_config.value["is_trusted_platform_module_enabled"]
      numa_nodes_per_socket              = platform_config.value["numa_nodes_per_socket"]
    }
  }

  shape_config {
    #Optional
    baseline_ocpu_utilization = var.baseline_ocpu_utilization
    memory_in_gbs             = var.memory_in_gbs == null ? local.shapes_config[var.shape]["memory_in_gbs"] : var.memory_in_gbs
    ocpus                     = var.ocpu_count == null ? local.shapes_config[var.shape]["ocpus"] : var.ocpu_count
  }

  source_details {
    source_id   = length(regexall("ocid1.image.oc1*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc1*", var.source_image_id)) > 0 || var.source_image_id == null ? var.source_image_id : data.oci_core_app_catalog_listing_resource_version.catalog_listing.0.listing_resource_id
    source_type = var.source_type
    #Optional
    #boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
    boot_volume_size_in_gbs = var.source_type == "image" ? var.boot_volume_size_in_gbs : null
    kms_key_id              = var.kms_key_id
  }

  lifecycle {
    ignore_changes = [create_vnic_details[0].defined_tags["Oracle-Tags.CreatedOn"], create_vnic_details[0].defined_tags["Oracle-Tags.CreatedBy"]]
  }
}

// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

####################################
## Resource Boot Volume - Backup Policy
## Create Boot Volume Backup Policy
####################################

locals {
  policy_tf_compartment_id = var.policy_tf_compartment_id != null && var.policy_tf_compartment_id != "" ? var.policy_tf_compartment_id : null
  current_policy_id        = var.boot_tf_policy != null ? (lower(var.boot_tf_policy) == "gold" || lower(var.boot_tf_policy) == "silver" || lower(var.boot_tf_policy) == "bronze" ? data.oci_core_volume_backup_policies.boot_vol_backup_policy[0].volume_backup_policies.0.id : data.oci_core_volume_backup_policies.boot_vol_custom_policy[0].volume_backup_policies.0.id) : null
}

resource "oci_core_volume_backup_policy_assignment" "volume_backup_policy_assignment" {
  depends_on = [oci_core_instance.instance]
  count      = var.boot_tf_policy != null ? 1 : 0
  #asset_id  = data.oci_core_boot_volumes.all_boot_volumes[0].boot_volumes.0.id
  asset_id  = oci_core_instance.instance.boot_volume_id
  policy_id = local.current_policy_id
  lifecycle {
    create_before_destroy = true
  }
}

################################
# Resource Block - Instances
# Market Place Images
################################

resource "oci_marketplace_accepted_agreement" "accepted_agreement" {
  count = length(regexall("ocid1.image.oc1*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc1*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  #Required
  agreement_id    = oci_marketplace_listing_package_agreement.listing_package_agreement.0.agreement_id
  compartment_id  = var.compartment_id
  listing_id      = data.oci_marketplace_listing.listing.0.id
  package_version = data.oci_marketplace_listing.listing.0.default_package_version
  signature       = oci_marketplace_listing_package_agreement.listing_package_agreement.0.signature
}

resource "oci_marketplace_listing_package_agreement" "listing_package_agreement" {
  count = length(regexall("ocid1.image.oc1*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc1*", var.source_image_id)) > 0  || var.source_image_id == null ? 0 : 1
  #Required
  agreement_id    = data.oci_marketplace_listing_package_agreements.listing_package_agreements.0.agreements[0].id
  listing_id      = data.oci_marketplace_listing.listing.0.id
  package_version = data.oci_marketplace_listing.listing.0.default_package_version
}