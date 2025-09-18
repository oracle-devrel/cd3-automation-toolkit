# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
    user_data           = fileexists("${path.root}/scripts/${local.cloud_init_script}") ? "${base64encode(file("${path.root}/scripts/${local.cloud_init_script}"))}" : null
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
      for_each =  local.plugins_config
      content {
        desired_state = plugins_config.value
        name          = plugins_config.key
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

  dynamic launch_options {
     #Check network_type exist
     for_each = var.launch_options != null ? (lookup(element(var.launch_options,0), "network_type", null) != null ? var.launch_options : []) : []

     content {
       #Optional
       #boot_volume_type                   = launch_options.value.boot_volume_type
       firmware                            = lookup(element(var.launch_options,0), "firmware", null)  != null ? launch_options.value.firmware : null
       is_consistent_volume_naming_enabled = lookup(element(var.launch_options,0), "is_consistent_volume_naming_enabled", null)  != null ? launch_options.value.is_consistent_volume_naming_enabled : null
       is_pv_encryption_in_transit_enabled = lookup(element(var.launch_options,0), "is_pv_encryption_in_transit_enabled", null)  != null ? launch_options.value.is_pv_encryption_in_transit_enabled : null
       network_type                        = launch_options.value.network_type
       #remote_data_volume_type            = launch_options.value.remote_data_volume_type
     }
   }

  dynamic "platform_config" {
    for_each = var.platform_config != null ? var.platform_config : []
    content {
      #Required
      type = lookup(element(var.platform_config,0),"config_type",null ) != "" ? platform_config.value.config_type : local.platform_configs[var.shape]["config_type"]
      #Optional
      is_measured_boot_enabled           = lookup(element(var.platform_config,0), "is_measured_boot_enabled", null)  != null ?  platform_config.value.is_measured_boot_enabled : null
      is_secure_boot_enabled             = lookup(element(var.platform_config,0), "is_secure_boot_enabled", null)  != null ? platform_config.value.is_secure_boot_enabled : null
      is_trusted_platform_module_enabled = lookup(element(var.platform_config,0), "is_trusted_platform_module_enabled", null)  != null ? platform_config.value.is_trusted_platform_module_enabled : null
      numa_nodes_per_socket              = lookup(element(var.platform_config,0), "numa_nodes_per_socket", null)  != null ? platform_config.value.numa_nodes_per_socket : null
    }
  }

  shape_config {
    #Optional
    baseline_ocpu_utilization = var.baseline_ocpu_utilization
    memory_in_gbs             = var.memory_in_gbs == null ? local.shapes_config[var.shape]["memory_in_gbs"] : var.memory_in_gbs
    ocpus                     = var.ocpu_count == null ? local.shapes_config[var.shape]["ocpus"] : var.ocpu_count
  }

  source_details {
    source_id   = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? var.source_image_id : data.oci_core_app_catalog_listing_resource_version.catalog_listing.0.listing_resource_id
    source_type = var.source_type
    #Optional
    #boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
    boot_volume_size_in_gbs = var.source_type == "image" ? var.boot_volume_size_in_gbs : null
    kms_key_id              = var.kms_key_id
  }

  lifecycle {
    ignore_changes = [create_vnic_details[0].defined_tags["Oracle-Tags.CreatedOn"], create_vnic_details[0].defined_tags["Oracle-Tags.CreatedBy"],metadata,extended_metadata]
  }
}


resource "null_resource" "ansible-remote-exec" {
  count = var.remote_execute == null ? 0 : ((length(regexall(".yaml", local.remote_execute_script)) > 0) || (length(regexall(".yml", local.remote_execute_script)) > 0) ? 1 : 0)

  connection {
    type        = "ssh"
    timeout     = "10m"
    agent       = false
    host        = oci_core_instance.instance.private_ip
    user        = "opc"
    private_key = fileexists("${path.root}/scripts/server-ssh-key") ? file("${path.root}/scripts/server-ssh-key") : ""

    bastion_host        = var.bastion_ip
    bastion_user        = "opc"
    bastion_private_key = fileexists("${path.root}/scripts/bastion-ssh-key") ? file("${path.root}/scripts/bastion-ssh-key") : ""
  }

  #This has been tested only OL8 version. For other OS it might need changes accordingly.
  provisioner "file" {
    source      = fileexists("${path.root}/scripts/${local.remote_execute_script}") ? "${path.root}/scripts/${local.remote_execute_script}" : "${path.root}/scripts/default.yaml"
    destination = "/home/opc/${local.remote_execute_script}"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo dnf install -y epel-release",
      "sudo dnf install ansible -y",
      "sudo ansible-galaxy collection install community.general",
      "sudo ansible-galaxy collection install ansible.posix",
      "sudo ansible --version",
      "sudo chmod 777 /home/opc/${local.remote_execute_script}",
      "sudo touch /etc/cron.d/ansible",
      "sudo chmod 600 /etc/cron.d/ansible",
      "sudo /bin/bash -c '/bin/echo \"* * * * * root ansible-playbook /home/opc/${local.remote_execute_script}\" >> /etc/cron.d/ansible'"
      #"sudo /bin/bash -c '/bin/echo \"1 * * * * root nice -n -20 ansible-playbook /home/opc/${local.remote_execute_script}\" >> /etc/cron.d/ansible'"
      #"sudo /bin/bash -c '/bin/echo \"2 * * * * sudo ansible-playbook /home/opc/${local.remote_execute_script} >> /home/opc/ansible.log 2>&1\" >> /etc/crontab'"
    ]
  }
}

resource "null_resource" "shell-remote-exec" {
  count = var.remote_execute == null ? 0 : ((length(regexall(".sh", local.remote_execute_script)) > 0) ? 1 : 0)
  connection {
    type        = "ssh"
    agent       = false
    timeout     = "10m"
    host        = oci_core_instance.instance.private_ip
    user        = "opc"
    private_key = fileexists("${path.root}/scripts/server-ssh-key") ? file("${path.root}/scripts/server-ssh-key") : ""

    bastion_host        = var.bastion_ip
    bastion_user        = "opc"
    bastion_private_key = fileexists("${path.root}/scripts/bastion-ssh-key") ? file("${path.root}/scripts/bastion-ssh-key") : ""
  }
  #Enable to remotely execute a shell script.
  provisioner "file" {
    source      = fileexists("${path.root}/scripts/${local.remote_execute_script}") ? "${path.root}/scripts/${local.remote_execute_script}" : "${path.root}/scripts/default.sh"
    destination = "/home/opc/${local.remote_execute_script}"
  }
  provisioner "remote-exec" {
    inline = [
      "chmod 777 /home/opc/${local.remote_execute_script}",
      "sudo yum install -y dos2unix",
      "dos2unix /home/opc/${local.remote_execute_script}",
      "/home/opc/${local.remote_execute_script}"
    ]
  }
}


# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
    ignore_changes        = [timeouts]
  }
}

################################
# Resource Block - Instances
# Market Place Images
################################

resource "oci_marketplace_accepted_agreement" "accepted_agreement" {
  count = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  #Required
  agreement_id    = oci_marketplace_listing_package_agreement.listing_package_agreement.0.agreement_id
  compartment_id  = var.compartment_id
  listing_id      = data.oci_marketplace_listing.listing.0.id
  package_version = data.oci_marketplace_listing.listing.0.default_package_version
  signature       = oci_marketplace_listing_package_agreement.listing_package_agreement.0.signature
}

resource "oci_marketplace_listing_package_agreement" "listing_package_agreement" {
  count = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  #Required
  agreement_id    = data.oci_marketplace_listing_package_agreements.listing_package_agreements.0.agreements[0].id
  listing_id      = data.oci_marketplace_listing.listing.0.id
  package_version = data.oci_marketplace_listing.listing.0.default_package_version
}

#------ Get Image Agreement 
resource "oci_core_app_catalog_listing_resource_version_agreement" "mp_image_agreement" {
  count      = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  listing_id = data.oci_marketplace_listing_package.listing_package.0.app_catalog_listing_id
  #listing_resource_version = data.oci_marketplace_listing_package.listing_package.0.app_catalog_listing_resource_version
  listing_resource_version = data.oci_core_app_catalog_listing_resource_versions.app_catalog_listing_resource_versions.0.app_catalog_listing_resource_versions[0].listing_resource_version
}



# ------ Accept Terms and Subscribe to the image, placing the image in a particular compartment
resource "oci_core_app_catalog_subscription" "mp_image_subscription" {
  count                    = length(regexall("ocid1.image.oc*", var.source_image_id)) > 0 || length(regexall("ocid1.bootvolume.oc*", var.source_image_id)) > 0 || var.source_image_id == null ? 0 : 1
  compartment_id           = var.compartment_id
  eula_link                = oci_core_app_catalog_listing_resource_version_agreement.mp_image_agreement[0].eula_link
  listing_id               = oci_core_app_catalog_listing_resource_version_agreement.mp_image_agreement[0].listing_id
  listing_resource_version = oci_core_app_catalog_listing_resource_version_agreement.mp_image_agreement[0].listing_resource_version
  oracle_terms_of_use_link = oci_core_app_catalog_listing_resource_version_agreement.mp_image_agreement[0].oracle_terms_of_use_link
  signature                = oci_core_app_catalog_listing_resource_version_agreement.mp_image_agreement[0].signature
  time_retrieved           = oci_core_app_catalog_listing_resource_version_agreement.mp_image_agreement[0].time_retrieved

  timeouts {
    create = "20m"
  }
}