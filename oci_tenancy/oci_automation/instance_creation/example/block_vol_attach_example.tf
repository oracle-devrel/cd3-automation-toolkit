resource "oci_core_volume"  "ocioraebsap601_blk_vol1"  {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.2.name}"
        compartment_id = "${var.compartment_ocid}"

        #Optional
        display_name = "ocioraebsap601_blk_vol1"
        size_in_gbs = "300"
        }

        resource "oci_core_volume_attachment" "ocioraebsap601_blk_vol1_volume_attachment" {
        #Required
        instance_id = "${oci_core_instance.ocioraebsap601.id}"
        attachment_type = "paravirtualized"
        volume_id = "${oci_core_volume.ocioraebsap601_blk_vol1.id}"

        }
