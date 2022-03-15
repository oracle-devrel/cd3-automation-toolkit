// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - BlockVolume
# Create BlockVolume
############################

module "blockvolume" {
  source   = "./modules/storage/blockvolume/blockvolume"
  depends_on = [module.instances]
  for_each = var.blockvolumes != null ? var.blockvolumes : {}
  attachment_type            = each.value.attachment_type
  attach_to_instance         = each.value.attach_to_instance != "" ? each.value.attach_to_instance : ""
  availability_domain        = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id             = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  vpus_per_gb                = each.value.vpus_per_gb != null ? each.value.vpus_per_gb : null
  defined_tags               = each.value.defined_tags
  display_name               = each.value.display_name
  freeform_tags              = each.value.freeform_tags
  is_auto_tune_enabled       = each.value.is_auto_tune_enabled
  kms_key_id                 = each.value.kms_key_id
  size_in_gbs                = each.value.size_in_gbs != null ? each.value.size_in_gbs : null
}

#######################################
# Module Block - BlockVolume
# Create Backup Policy For Block Volume
#######################################

module "block-backup-policy" {
  depends_on = [module.blockvolume]
  source = "./modules/storage/blockvolume/backup-policy"
  for_each = var.block_backup_policies != null ? var.block_backup_policies : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name = each.value.display_name
  block_tf_policy = each.value.backup_policy != "" ? each.value.backup_policy : ""
  defined_tags = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  policy_tf_compartment_id = each.value.policy_tf_compartment_id != "" ? (length(regexall("ocid1.compartment.oc1*", each.value.policy_tf_compartment_id)) > 0 ? each.value.policy_tf_compartment_id : var.compartment_ocids[each.value.policy_tf_compartment_id]) : ""
}