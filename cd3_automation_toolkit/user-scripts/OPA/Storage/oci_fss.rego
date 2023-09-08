package terraform
import input as tfplan


#Ensure FSS are encrypted with CMK

deny[reason] {
	r = tfplan.resource_changes[_]
	r.mode == "managed"
	r.type == "oci_file_storage_file_system"
	r.change.after.kms_key_id == null

    allow := false
	reason := sprintf("%-10s%-10s :: OCI FSS must be encrypted with CMK as per CIS standard's",
	                    [allow, r.address])
}
