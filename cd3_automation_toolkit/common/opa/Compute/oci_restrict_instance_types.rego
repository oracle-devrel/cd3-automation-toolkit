#################################
# OCI restricting instance types#
#################################

package terraform

import input as tfplan

# Define a set of allowed instance types
allowed_instance_types = {
    "VM.Standard2.1",
    "VM.Standard2.2",
    "VM.Standard2.4",
    "VM.Standard2.8",
    "BM.Standard2.52",
    "BM.DenseIO2.52",
    "BM.GPU2.2"
}

default allow = false

# Deny creation of instances with disallowed instance types
deny_instances {
    input.resource.type == "oci_compute_instance"
    instance_type := input.resource.conf.instance_type
    not instance_type.allowed_instance_types[instance_type]
}

# Allow all other resource types
allow {
    not deny_instances
}