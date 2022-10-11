// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - BlockVolume
# Create BlockVolume and Block Volume Backup Policy
############################

#data "oci_core_instances" "instance" {
#  depends_on = [module.instances]
#  for_each       = var.blockvolumes != null ? var.blockvolumes : {}
#  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
#  display_name   =  one(each.value.attach_to_instance)
#  state = "RUNNING"
#}

module "block-volumes" {
  source             = "./modules/storage/block-volume"
  for_each           = var.blockvolumes != null ? var.blockvolumes : {}
  attachment_type    = each.value.attachment_type
  attach_to_instance = each.value.attach_to_instance != "" ? length(regexall("ocid1.instance.oc1*", each.value.attach_to_instance)) > 0 ? each.value.attach_to_instance : merge(module.instances.*...)[each.value.attach_to_instance]["instance_tf_id"] : ""
  #attach_to_instance  = length(each.value.attach_to_instance) > 0 ? [data.oci_core_instances.instance[each.value.display_name].instances[0].id] : []
  availability_domain      = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id           = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vpus_per_gb              = each.value.vpus_per_gb != null ? each.value.vpus_per_gb : null
  device                   = each.value.device
  defined_tags             = each.value.defined_tags
  display_name             = each.value.display_name
  freeform_tags            = each.value.freeform_tags
  is_auto_tune_enabled     = each.value.is_auto_tune_enabled
  kms_key_id               = each.value.kms_key_id
  size_in_gbs              = each.value.size_in_gbs != null ? each.value.size_in_gbs : null
  block_tf_policy          = each.value.backup_policy != "" ? each.value.backup_policy : ""
  policy_tf_compartment_id = each.value.policy_compartment_id != "" ? (length(regexall("ocid1.compartment.oc1*", each.value.policy_compartment_id)) > 0 ? each.value.policy_compartment_id : var.compartment_ocids[each.value.policy_compartment_id]) : ""


  #Volume Attachment Optional Params
  #  attachment_display_name   = each.value.attachment_display_name
  #  encryption_in_transit_type          = each.value.encryption_in_transit_type                  # Applicable when attachment_type=iscsi
  is_pv_encryption_in_transit_enabled = each.value.is_pv_encryption_in_transit_enabled # Applicable when attachment_type=paravirtualized
  #  is_read_only              = each.value.is_read_only
  #  is_shareable              = each.value.is_shareable
  #  use_chap                  = each.value.use_chap
}
