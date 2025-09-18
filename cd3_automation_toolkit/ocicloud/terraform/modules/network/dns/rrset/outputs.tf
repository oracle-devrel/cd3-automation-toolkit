# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Outputs Block - Steering Policy #
############################

output "rrset_id" {
  value = oci_dns_rrset.rrset.id
}