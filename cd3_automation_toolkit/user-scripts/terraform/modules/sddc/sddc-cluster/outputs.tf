// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Custom Backup Policy
# Create Custom Backup Policy
############################



output "sddc_cluster_tf_id" {
  value = oci_ocvp_cluster.sddc_cluster.id
}
