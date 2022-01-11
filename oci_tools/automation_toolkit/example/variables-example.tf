variable "ssh_public_key" {
	type = string
	default = "<YOUR SSH PUB KEY STRING HERE>"
}

variable "tenancy_ocid" {
        type = string
        default = "<YOUR TENANCY OCID HERE>"
}

variable "user_ocid" {
        type = string
        default = "<USER OCID HERE>"
}

variable "fingerprint" {
        type = string
        default = "<SSH KEY FINGERPRINT> - Use the create_keys.sh for easily creating keys and its fingerprint> "
}

variable "private_key_path" {
        type = string
        default = "<The Private key file path> - If you've used the createPEMKeys.py then the full path of where the .pem file is>"
}

variable "region" {
        type = string
        default = "<OCI Tenancy Region where these objects will be created - us-phoenix-1 or us-ashburn-1>"
}

        #################################
        #
        # Variables according to Services
        #
        #################################

        ############################
        ### Fetch Compartments #####
        ############################

        ## Do Not Modify #START_Compartment_OCIDs#
        variable "compartment_ocids" {
            type = list(any)
            default = [{}]
        }
        #Compartment_OCIDs_END#  ## Do Not Modify

        #########################
        ##### Identity ##########
        #########################

        variable "compartments" {
          type    = map(any)
          default = {}
        }

        variable "policies" {
          type    = map(any)
          default = {}
        }

        variable "groups" {
          type    = map(any)
          default = {}
        }

        #########################
        ##### Network ########
        #########################

        variable "default_dhcps" {
          type = map(any)
          default = {}
        }

        variable "vcns" {
          type    = map(any)
          default = {}
        }

        variable "igws" {
          type    = map(any)
          default = {}
        }

        variable "sgws" {
          type    = map(any)
          default = {}
        }

        variable "ngws" {
          type    = map(any)
          default = {}
        }

        variable "hub-lpgs" {
          type    = map(any)
          default = {}
        }

        variable "spoke-lpgs" {
          type    = map(any)
          default = {}
        }

