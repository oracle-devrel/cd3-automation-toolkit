resource "oci_core_instance" "##Hostname##" {
        #Required
        #availability_domain = "##Availability Domain##"
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.##Availability Domain##.name}"
        compartment_id = "${var.compartment_ocid}"
### windows image id - oci image ###
       # image = "${var.windows2008_image_ocid}"
        source_details {
	        source_id  = "${var.windows2008_image_ocid}"
                source_type = "image"
        }
	shape = "##Shape##"


        #Optional
        create_vnic_details {
                #Required
                subnet_id = "${oci_core_subnet.##subnet name##.id}"
                assign_public_ip = ##Pub Address##

                #Optional
                display_name = "##Hostname##"
                hostname_label = "##Hostname##"
                private_ip = "##IP Address##"
                skip_source_dest_check = false
        }
        display_name = "##Hostname##"
        hostname_label = "##Hostname##"
        subnet_id = "${oci_core_subnet.##subnet name##.id}"
}
