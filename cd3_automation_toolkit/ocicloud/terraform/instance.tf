# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Module Block - Instances
## Create Instance
#############################

data "oci_core_subnets" "oci_subnets" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.instances != null ? var.instances : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns" {
  # depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each       = var.instances != null ? var.instances : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "instances" {
  source = "./modules/compute/instance"
  # depends_on = [module.nsgs] # Uncomment to create NSG and Instances together
  for_each               = var.instances != null ? var.instances : {}
  availability_domain    = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id         = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
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
  source_image_id        = length(regexall("ocid1.image.oc*", each.value.source_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", each.value.source_id)) > 0 ? each.value.source_id : lookup(var.instance_source_ocids, each.value.source_id, null)
  subnet_id              = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets[each.key].subnets.*.id[0]) : null
  assign_public_ip       = each.value.assign_public_ip
  ssh_public_keys        = each.value.ssh_authorized_keys != null ? (length(regexall("ssh-rsa*", each.value.ssh_authorized_keys)) > 0 ? each.value.ssh_authorized_keys : lookup(var.instance_ssh_keys, each.value.ssh_authorized_keys, null)) : null
  hostname_label         = each.value.hostname_label
  nsg_ids                = each.value.nsg_ids
  #nsg_ids              = each.value.nsg_ids != [] ? [for nsg in each.value.nsg_ids : length(regexall("ocid1.networksecuritygroup.oc*",nsg)) > 0 ? nsg : merge(module.nsgs.*...)[nsg]["nsg_tf_id"]] : []
  boot_volume_size_in_gbs                    = each.value.boot_volume_size_in_gbs != null ? each.value.boot_volume_size_in_gbs : null
  memory_in_gbs                              = each.value.memory_in_gbs != null ? each.value.memory_in_gbs : null
  capacity_reservation_id                    = each.value.capacity_reservation_id != null ? (length(regexall("ocid1.capacityreservation.oc*", each.value.capacity_reservation_id)) > 0 ? each.value.capacity_reservation_id : lookup(var.capacity_reservation_ocids, each.value.capacity_reservation_id, null)) : null
  create_is_pv_encryption_in_transit_enabled = each.value.create_is_pv_encryption_in_transit_enabled

  boot_tf_policy              = each.value.backup_policy != null ? each.value.backup_policy : null
  policy_tf_compartment_id    = each.value.policy_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.policy_compartment_id)) > 0 ? each.value.policy_compartment_id : var.compartment_ocids[each.value.policy_compartment_id]) : null
  remote_execute              = each.value.remote_execute != null ? each.value.remote_execute : null
  bastion_ip                  = each.value.bastion_ip != null ? each.value.bastion_ip : null
  cloud_init_script           = each.value.cloud_init_script != null ? each.value.cloud_init_script : null
  launch_options              = each.value.launch_options
  plugins_details             = each.value.plugins_details
  platform_config             = each.value.platform_config != null ? each.value.platform_config : null
  is_live_migration_preferred = each.value.is_live_migration_preferred

  # extended_metadata    = each.value.extended_metadata
  skip_source_dest_check    = each.value.skip_source_dest_check != null ? each.value.skip_source_dest_check : null
  baseline_ocpu_utilization = each.value.baseline_ocpu_utilization
  # preemptible_instance_config = each.value.preemptible_instance_config
  all_plugins_disabled               = each.value.all_plugins_disabled
  is_management_disabled             = each.value.is_management_disabled
  is_monitoring_disabled             = each.value.is_monitoring_disabled
  recovery_action                    = each.value.recovery_action
  are_legacy_imds_endpoints_disabled = each.value.are_legacy_imds_endpoints_disabled
  ipxe_script                        = each.value.ipxe_script
  preserve_boot_volume               = each.value.preserve_boot_volume
  assign_private_dns_record          = each.value.assign_private_dns_record
  vlan_id                            = each.value.vlan_id
  kms_key_id                         = each.value.kms_key_id

  # VNIC Details
  vnic_defined_tags  = each.value.vnic_defined_tags
  vnic_freeform_tags = each.value.vnic_freeform_tags
  vnic_display_name  = each.value.vnic_display_name
}
