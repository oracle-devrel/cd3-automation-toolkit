##############################
# OCI bucket public deny rule#
##############################


package terraform

import input as tfplan


deny[reason] {
	r = tfplan.resource_changes[_]
	r.mode == "managed"
	r.type == "oci_objectstorage_bucket"
	r.change.after.access_type == "ObjectRead"

	reason := sprintf("%-40s :: CIS Violation - OCI buckets must not be PUBLIC",
	                    [r.address])
}
