# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Outputs Block - Custom Backup Policy
# Create Custom Backup Policy
############################



output "sddc_cluster_tf_id" {
  value = oci_ocvp_cluster.sddc_cluster.id
}
