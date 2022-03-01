// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Output Block - Network
# Create Subnets
#############################

output "subnet_id" {
  value = zipmap(oci_core_subnet.subnet.*.display_name,oci_core_subnet.subnet.*.id)
}

output "ads" {
  value = data.oci_identity_availability_domains.availability_domains.availability_domains.*.name
}

output "subnet_tf_id" {
  value = oci_core_subnet.subnet.*.id
}