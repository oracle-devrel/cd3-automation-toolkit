// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Security
## Create Key
################################

output "key_tf_id" {
  value = oci_kms_key.key.id
}