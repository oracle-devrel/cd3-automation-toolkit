variable "ssh_public_key" {
	type = "string"
	default = "<YOUR SSH PUB KEY STRING HERE>"

}

variable "tenancy_ocid" {
        type = "string"
        default = "<YOUR TENANCY OCID HERE>"
}

variable "user_ocid" {
        type = "string"
        default = "<USER OCID HERE>
}

variable "compartment_ocid" {
        type = "string"
        default = "<CORE COMPARTMENT FOR OBJECTS HERE>"
}

variable "ntk_compartment_ocid" {
        type = "string"
        default = "<COMPARTMENT FOR ALL NETWORK OBJECTS HERE - can be the same ocid as compartment_ocid>"
}
variable "fingerprint" {
        type = "string"
        default = "<SSH KEY FINGERPRINT> - Use the create_keys.sh for easily creating keys and its fingerprint "
}
variable "private_key_path" {
        type = "string"
        default = "<The Private key file path> - If you've used the create_keys.sh then the full path of where the .pem file is>"
}

variable "region" {
        type = "string"
        default = "<OCI Tenancy Region where these objects will be created - us-phoenix-1 or us-ashburn-1>"
}


