// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - VLAN
# Create VLANs
############################

output "custom_vlan_tf_id" {
  value = oci_core_vlan.vlan.id
}

