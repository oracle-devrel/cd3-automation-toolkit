# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Governance
# Create Quota Policies
############################

resource "oci_limits_quota" "quota" {
    #Required
    compartment_id = var.tenancy_ocid
    description = var.quota_description
    name = var.quota_name
    statements = var.quota_statements

    #Optional
    defined_tags             = var.defined_tags
    freeform_tags            = var.freeform_tags
    #locks {
    #    #Required
    #    type = var.quota_locks_type

    #    #Optional
    #    message = var.quota_locks_message
    #    #related_resource_id = oci_limits_related_resource.test_related_resource.id
    #}
}