package terraform

#Ensure no object storage buckets are publicly visible.
#Ensure object storage buckets are encrypted with a CMK.
#Ensure versioning is enabled for buckets.
import input as tfplan


deny[reason] {
	r = tfplan.resource_changes[_]
	r.mode == "managed"
	r.type == "oci_objectstorage_bucket"
	r.change.after.access_type == "ObjectRead"
#	r.change.after.kms_key_id == null
#    r.change.after.versioning == "Disabled"

	reason := sprintf("%-40s :: OCI buckets must be private as per CIS standard's",
	                    [r.address])
}

deny[reason] {
	r = tfplan.resource_changes[_]
	r.mode == "managed"
	r.type == "oci_objectstorage_bucket"
	r.change.after.kms_key_id == null

	reason := sprintf("%-40s :: OCI buckets must be encrypted with CMK as per CIS standard's",
	                    [r.address])
}

deny[reason] {
	r = tfplan.resource_changes[_]
	r.mode == "managed"
	r.type == "oci_objectstorage_bucket"
   r.change.after.versioning == "Disabled"

	reason := sprintf("%-40s :: OCI buckets should be private/versioning enabled/encrypted with CMK as per CIS standard's",
	                    [r.address])
}

#To enforce encryption at rest for object storage:
default enforce_object_storage_encryption = false

enforce_object_storage_encryption {
    bucket := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    bucket.type == "oci_objectstorage_bucket"

    bucket.is_encryption_enabled
    bucket.is_encryption_in_transit_enabled
    #bucket.defined_tags["cis.cis-benchmark"] == "true"
}

#To enforce secure storage configuration for object storage
default enforce_object_storage_config = false

enforce_object_storage_config {
    bucket := input.planned_values.root_module.child_modules[_].resources[_].instances[_].attributes
    bucket.type == "oci_objectstorage_bucket"

    bucket.is_public_access_allowed == false
    bucket.are_server_side_encryption_rules_enabled
    #bucket.defined_tags["cis.cis-benchmark"] == "true"
}