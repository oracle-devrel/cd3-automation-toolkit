// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Module Block - Instances
## Create Instance
#############################

module "instances" {
  source                 = "./modules/compute/instance"
  for_each               = var.instances != null ? var.instances : {}
  availability_domain    = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id         = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  vcn_names              = [each.value.vcn_name]
  dedicated_vm_host_name = each.value.dedicated_vm_host_id != null ? each.value.dedicated_vm_host_id : null
  shape                  = each.value.shape
  ocpu_count             = each.value.ocpus
  private_ip             = each.value.private_ip != null ? each.value.private_ip : null
  defined_tags           = each.value.defined_tags
  display_name           = each.value.display_name
  fault_domain           = each.value.fault_domain
  freeform_tags          = each.value.freeform_tags
  source_type            = each.value.source_type
  source_image_id        = length(regexall("ocid1.image.oc1*", each.value.source_id)) > 0 || length(regexall("ocid1.bootvolume.oc1*", each.value.source_id)) > 0 ? each.value.source_id : lookup(var.instance_source_ocids, each.value.source_id, null)
  subnet_id              = each.value.subnet_id
  assign_public_ip       = each.value.assign_public_ip
  ssh_public_keys        = each.value.ssh_authorized_keys!= null? (length(regexall("ssh-rsa*", each.value.ssh_authorized_keys)) > 0 ? each.value.ssh_authorized_keys : lookup(var.instance_ssh_keys, each.value.ssh_authorized_keys, null)) : null
  hostname_label         = each.value.hostname_label
  nsg_ids                = each.value.nsg_ids != null ? each.value.nsg_ids : []
  #nsg_ids              = each.value.nsg_ids != [] ? [for nsg in each.value.nsg_ids : length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : merge(module.nsgs.*...)[nsg]["nsg_tf_id"]] : []
  boot_volume_size_in_gbs                    = each.value.boot_volume_size_in_gbs != null ? each.value.boot_volume_size_in_gbs : null
  memory_in_gbs                              = each.value.memory_in_gbs != null ? each.value.memory_in_gbs : null
  capacity_reservation_id                    = each.value.capacity_reservation_id != null ? lookup(var.capacity_reservation_ocids, each.value.capacity_reservation_id, null) : null
  create_is_pv_encryption_in_transit_enabled = each.value.create_is_pv_encryption_in_transit_enabled
  update_is_pv_encryption_in_transit_enabled = each.value.update_is_pv_encryption_in_transit_enabled

  boot_tf_policy           = each.value.backup_policy != null ? each.value.backup_policy : null
  policy_tf_compartment_id = each.value.policy_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.policy_compartment_id)) > 0 ? each.value.policy_compartment_id : var.compartment_ocids[each.value.policy_compartment_id]) : null

  ## Optional parameters to enable and test ##
  # extended_metadata    = each.value.extended_metadata
  # skip_source_dest_check = each.value.skip_source_dest_check != null ? each.value.skip_source_dest_check : null
  # baseline_ocpu_utilization = each.value.baseline_ocpu_utilization
  # preemptible_instance_config = each.value.preemptible_instance_config
  # all_plugins_disabled = each.value.all_plugins_disabled
  # is_management_disabled  = each.value.is_management_disabled
  # is_monitoring_disabled = each.value.is_monitoring_disabled
  # plugins_details = each.value.plugins_details
  # is_live_migration_preferred = each.value.is_live_migration_preferred
  # recovery_action = each.value.recovery_action
  # are_legacy_imds_endpoints_disabled = each.value.are_legacy_imds_endpoints_disabled
  # boot_volume_type = each.value.boot_volume_type
  # firmware = each.value.firmware
  # is_consistent_volume_naming_enabled = each.value.is_consistent_volume_naming_enabled
  # network_type = each.value.network_type
  # remote_data_volume_type = each.value.remote_data_volume_type
  # platform_config = each.value.platform_config
  # ipxe_script = each.value.ipxe_script
  # preserve_boot_volume = each.value.preserve_boot_volume
  # assign_private_dns_record = each.value.assign_private_dns_record
  # vlan_id = each.value.vlan_id
  # kms_key_id = each.value.kms_key_id

  # VNIC Details
  # vnic_defined_tags = each.value.vnic_defined_tags
  # vnic_freeform_tags = each.value.vnic_freeform_tags
  # vnic_display_name = each.value.vnic_display_name
}

