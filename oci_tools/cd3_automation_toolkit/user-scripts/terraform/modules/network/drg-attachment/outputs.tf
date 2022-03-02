// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Dynamic Routing Gateway Attachment
############################

output "drg_attachment_tf_id" {
  value = oci_core_drg_attachment.drg_attachment.id
}
