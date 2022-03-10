// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Instance
# Create Instance
############################

output "instance_tf_id" {
  value = oci_core_instance.core_instance.id
}