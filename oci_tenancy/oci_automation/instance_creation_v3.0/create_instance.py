#!/bin/bash
#
#
#        Property of Oracle Corp - Oracle Consulting Services
#                 Do not copy or distribute unpublished work
#                             All Rights Reserved
###############################################################################
# Customer acknowledges that the software script(s) are not a
# generally available standard Oracle Corp product and that it is a
# fundamental condition of supply of the software script(s) to
# Customer that Customer accepts the same "as is" and without
# warranty of any kind.  No support services of any kind are
# available for the software script(s) and Oracle Corp does not represent
# to Customer that:
#
# (i)   operation of any of the software script(s) shall be
#       uninterrupted or error free, or
#
# (ii)  functions contained in the software script(s) shall operate
#       in the combinations which may be selected for use by
#       Customer or meet Customer's requirements, or
#
# (iii) that upgraded versions of the software script(s) will be
#       issued.
#
# If Customer wishes to have the software script(s) modified, or
# otherwise requires support, Oracle Corp may provide the same by means of
# a separate consulting agreement priced on a time and materials
# basis.
#
##############################################################################
# Author:   Shruthi Subramanian
# Date:     April 24,2019
# Version:  1.0.0
#
# Required Inputs: info.csv and target directory
# Output: generation of Terraform file to launch an instance
#
##############################################################################
# Change history (most recent last)
#
# Version       When            	Who             		Comments
# -------       ----            	---             		--------
# 1.0.0         24 April 2019  		Shruthi Subramanian     Initial Draft of script
#
##############################################################################


import sys
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Create vars files for the each row in csv file.")
parser.add_argument("file", help="Full Path of csv file or CD3 excel file. eg instance.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir
ADS = ["AD1", "AD2", "AD3"]

#If input is CD3 excel file
if('.xlsx' in filename):
    df = pd.read_excel(filename, sheet_name='Instances')
    for i in df.index:
        compartment_id = df.iat[i, 0]
        hostname_label = df.iat[i, 1]
        display_name=hostname_label
        availability_domain = df.iat[i, 2]
        ad = ADS.index(availability_domain)
        fault_domain = df.iat[i, 3]
        subnet_name = df.iat[i, 4]
        assign_public_ip = df.iat[i, 5]
        assign_public_ip=str(assign_public_ip)
        assign_public_ip=assign_public_ip.lower()
        private_ip = df.iat[i, 6]
        source_name = df.iat[i, 7]
        shape = df.iat[i, 8]
        ssh_public_key = df.iat[i, 9]
        source_type="image"
        skip_source_dest_check="false"
        tempStr = """
resource "oci_core_instance" \"""" + hostname_label + """\" {
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var.""" + compartment_id + """}"
        fault_domain = \"""" + fault_domain + """\"
        source_details {
        	source_id  = "${var.""" + source_name + """}"
            source_type = \"""" + source_type + """\"
            }
            shape = \"""" + shape + """\"
                metadata {
                ssh_authorized_keys = "${var.""" + ssh_public_key + """}"
            }

            create_vnic_details {
                subnet_id = "${oci_core_subnet.""" + subnet_name + """.id}"
                assign_public_ip = \"""" + assign_public_ip + """\"
                display_name = \"""" + display_name + """\"
                hostname_label = \"""" + hostname_label + """\"
                private_ip =\"""" + private_ip + """\"
                skip_source_dest_check = \"""" + skip_source_dest_check + """\"
            }
            display_name = \"""" + display_name + """\"
            hostname_label = \"""" + hostname_label + """\"
            subnet_id = "${oci_core_subnet.""" + subnet_name + """.id}"
}
"""
        outfile = outdir + "/" + hostname_label + ".tf"
        oname = open(outfile, "w+")
        oname.write(tempStr)
        oname.close()

#If input is a csv file
if('.csv' in filename):
    fname = open(filename, "r")
    # Read csv file
    for line in fname:
        if not line.startswith('#'):
            # [availability_domain, compartment_name,imag_var_name, shape, subnet_name, display_name, hostname_label, private_ip, skip_source_dest_check,assign_public_ip,fault_domain,source_type,ssh_public_key] = line.split(',')
            linearr = line.split(",")
            availability_domain = linearr[0].strip()
            compartment_id = linearr[1].strip()
            source_name = linearr[2].strip()
            shape = linearr[3].strip()
            subnet_name = linearr[4].strip()
            display_name = linearr[5].strip()
            hostname_label = linearr[6].strip()
            private_ip = linearr[7].strip()
            skip_source_dest_check = linearr[8].strip().lower()
            assign_public_ip = linearr[9].strip().lower()
            fault_domain = linearr[10].strip()
            source_type = linearr[11].strip()
            ssh_public_key = linearr[12].strip()
            ad = ADS.index(availability_domain)
            tempStr = """
resource "oci_core_instance" \""""+hostname_label+"""\" {
		availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var."""+compartment_id+"""}"
        fault_domain = \"""" + fault_domain + """\"
        source_details {
	        source_id  = "${var."""+source_name+"""}"
            source_type = \"""" + source_type + """\"
        }
        shape = \"""" + shape + """\"
            metadata {
            ssh_authorized_keys = "${var."""+ssh_public_key+"""}"
        }

        create_vnic_details {
            subnet_id = "${oci_core_subnet."""+subnet_name+""".id}"
            assign_public_ip = \"""" + assign_public_ip + """\"
            display_name = \"""" + display_name + """\"
            hostname_label = \"""" + hostname_label + """\"
            private_ip =\"""" + private_ip + """\"
            skip_source_dest_check = \"""" + skip_source_dest_check + """\"
        }
        display_name = \"""" + display_name + """\"
        hostname_label = \"""" + hostname_label + """\"
        subnet_id = "${oci_core_subnet."""+subnet_name+""".id}"
}
"""
            outfile = outdir +"/"+hostname_label + ".tf"
            oname = open(outfile, "w+")
            oname.write(tempStr)
            oname.close()
    fname.close()