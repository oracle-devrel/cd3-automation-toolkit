#!/bin/python
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import argparse
import pandas as pd


parser = argparse.ArgumentParser(description="CSV filename")
parser.add_argument("file",help="Full Path to the CSV file for creating block volume or CD3 excel file. eg instance.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir",help="directory path for output tf files ")


if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir


ADS = ["AD1", "AD2", "AD3"]

#If input is CD3 excel file
if('.xls' in filename):

    df = pd.read_excel(filename, sheet_name='BlockVols')
    for i in df.index:
        blockname = df.iat[i, 0]
        size = df.iat[i, 1]
        size=str(size)
        AD = df.iat[i, 2]
        attacheToInstanceName = df.iat[i, 3]
        attachType = df.iat[i, 4]
        compartmentVarName = df.iat[i, 5]
        ad = ADS.index(AD)
        display_name = blockname

        tempStr = """resource "oci_core_volume"  \"""" + blockname + """"  {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var.""" + compartmentVarName + """}"

        #Optional
        display_name = \"""" + blockname + """"
        size_in_gbs = \"""" + size + """"
        ## Defined Tag Info ##
        }

resource "oci_core_volume_attachment" \"""" + blockname + """_volume_attachment" {
        #Required
        instance_id = "${oci_core_instance.""" + attacheToInstanceName + """.id}"
        attachment_type = \"""" + attachType + """"
        volume_id = "${oci_core_volume.""" + blockname + """.id}"

        }
        
        """
        outfile = outdir+"/"+blockname+".tf"
        print "Writing " + outfile
        oname = open(outfile,"w")
        oname.write(tempStr)
        oname.close()



#If input is a csv file
if('.csv' in filename):
    fname = open(filename, "r")

    for line in fname:
        if not line.startswith('#'):
            #[block_name,size_in_gb,availability_domain(AD1|AD2|AD3),attached_to_instance,attach_type(iscsi|paravirtualized,compartment_var_name] = line.split(',')
            linearr = line.split(",")
            blockname = linearr[0].strip()
            size = linearr[1].strip()
            AD = linearr[2].strip()
            attacheToInstanceName = linearr[3].strip()
            attachType = linearr[4].strip()
            compartmentVarName = linearr[5].strip()
            ad = ADS.index(AD)
            display_name = blockname

            tempStr = """resource "oci_core_volume"  \"""" + blockname + """"  {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var.""" + compartmentVarName + """}"

        #Optional
        display_name = \"""" + blockname + """"
        size_in_gbs = \"""" + size + """"
        }

resource "oci_core_volume_attachment" \"""" + blockname + """_volume_attachment" {
        #Required
        instance_id = "${oci_core_instance.""" + attacheToInstanceName + """.id}"
        attachment_type = \"""" + attachType + """"
        volume_id = "${oci_core_volume.""" + blockname + """.id}"

        }
        """
            outfile = outdir+"/"+blockname+".tf"
            print "Writing " + outfile
            oname = open(outfile,"w")
            oname.write(tempStr)
            oname.close()
    fname.close()

