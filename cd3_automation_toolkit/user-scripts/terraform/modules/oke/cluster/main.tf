# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_containerengine_cluster" "cluster" {
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = var.display_name
  vcn_id             = data.oci_core_vcns.oci_vcns_clusters[var.vcn_names[0]].virtual_networks.*.id[0]
  defined_tags       = var.defined_tags
  freeform_tags      = var.freeform_tags
  kms_key_id         = var.kms_key_id
  type               = var.type

  cluster_pod_network_options {
    #Required
    cni_type = var.cni_type
  }

  endpoint_config {
    is_public_ip_enabled = var.is_public_ip_enabled
    nsg_ids              = var.nsg_ids != null ? (local.endpoint_nsg_ids == [] ? ["INVALID ENDPOINT NSG Name"] : local.endpoint_nsg_ids) : null
    subnet_id            = var.endpoint_subnet_id
  }

  image_policy_config {
        #Optional
        is_policy_enabled = var.is_policy_enabled
        dynamic "key_details" {
            for_each = var.policy_kms_key_id != null ? [1] : []
            content{
            #Optional
            kms_key_id = var.policy_kms_key_id
            }
        }
    }

  options {
    add_ons {
      #Optional
      is_kubernetes_dashboard_enabled = var.is_kubernetes_dashboard_enabled
      is_tiller_enabled               = var.is_tiller_enabled
    }
    admission_controller_options {
      is_pod_security_policy_enabled = var.is_pod_security_policy_enabled
    }

    kubernetes_network_config {
      pods_cidr     = var.pods_cidr
      services_cidr = var.services_cidr
    }
    service_lb_subnet_ids = flatten(tolist([for subnet in var.service_lb_subnet_ids : (length(regexall("ocid1.subnet.oc*", subnet)) > 0 ? [subnet] : data.oci_core_subnets.oci_subnets_cluster_lbs[subnet].subnets[*].id)]))
    persistent_volume_config {
     #Optional
     defined_tags = var.volume_defined_tags
     freeform_tags = var.volume_freeform_tags
    }
    service_lb_config {
     #Optional
     defined_tags = var.lb_defined_tags
     freeform_tags = var.lb_freeform_tags
   }
 }
 lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"],timeouts]
  }
}
