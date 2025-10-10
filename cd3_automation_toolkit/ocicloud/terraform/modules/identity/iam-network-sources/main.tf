# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Identity
# Create network source
############################

resource "oci_identity_network_source" "network_source" {

  #Required
  compartment_id = var.tenancy_ocid
  description    = var.description
  name           = var.name
 
  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  
  #Optional
  public_source_list = var.public_source_list != null ? var.public_source_list : null
  
  #Optional
  dynamic "virtual_source_list" {
  for_each = { for k,v in var.virtual_source_list : k=> v}
	content {
		ip_ranges = virtual_source_list.value.ip_ranges
		vcn_id = "" #virtual_source_list.value.vcn_id       
		}
	}
	
	
	lifecycle {
    ignore_changes = [virtual_source_list[0].vcn_id,virtual_source_list[1].vcn_id, virtual_source_list[2].vcn_id,virtual_source_list[3].vcn_id,virtual_source_list[4].vcn_id,virtual_source_list[5].vcn_id,virtual_source_list[6].vcn_id]
  }

	

}

