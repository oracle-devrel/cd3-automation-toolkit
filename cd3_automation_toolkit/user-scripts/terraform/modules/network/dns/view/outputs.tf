# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Outputs Block - DNS view #
############################

output "views" {
  value = [for item in [oci_dns_view.view.id]:{"id" = "${item}"}]
}