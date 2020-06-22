resource "oci_core_instance" "##Hostname##" {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.##Availability Domain##.name}"
        compartment_id = "${var.##Compartment Name##}"
        shape = "##Shape##"
        shape_config {
                # Note: RAM = ocpus x 16GB
                # Note: # of vNICs = ocpus x 2
                ocpus = "##ocpus##"
        }


        #Optional
        fault_domain = "##Fault Domain##"
        source_details {
		        source_id  = "${var.linux_ocid}"
                source_type = "image"
        }
        create_vnic_details {
                #Required
                subnet_id = "${oci_core_subnet.##subnet name##.id}"
                hostname_label = "##Hostname##"
                #Optional
                assign_public_ip = ##Pub Address##
                display_name = "##Hostname##"
                private_ip = "##IP Address##"
                skip_source_dest_check = false

                ##NSGs##
        }

        ##DedicatedVMHost##

        display_name = "##Hostname##"

        metadata = {

				ssh_authorized_keys = "${var.##SSH-key-var-name##}"
        }
        subnet_id = "${oci_core_subnet.##subnet name##.id}"

        ## Defined Tag Info ##
}
