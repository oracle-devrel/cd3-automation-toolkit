// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Object Storage
## Create Object Storage
################################

output "bucket_tf_id" {
  value = oci_objectstorage_bucket.bucket.id
}