#!/usr/bin/python3
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import argparse
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../..")
from commonTools import *



parser = argparse.ArgumentParser(description="Creates TF files for Block Volumes")
parser.add_argument("file",help="Full Path to the CSV file for creating block volume or CD3 excel file. eg instance.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

ADS = ["AD1", "AD2", "AD3"]
endNames = {'<END>', '<end>','<End>'}

#If input is CD3 excel file
if('.xls' in filename):

    df = pd.read_excel(filename, sheet_name='BlockVols',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    for i in df.index:
        region=df.iat[i,0]
        region=region.strip().lower()
        if region in endNames:
            break
        if region not in ct.all_regions:
            print("Invalid Region; It should be one of the values tenancy is subscribed to")
            continue

        blockname = df.iat[i, 1]
        size = df.iat[i, 2]
        s=int(size)
        size=str(s)
        AD = df.iat[i, 3]
        AD=AD.upper()
        attacheToInstanceName = df.iat[i, 4]
        attachType = df.iat[i, 5]
        compartmentVarName = df.iat[i, 6]
        ad = ADS.index(AD)
        display_name = blockname

        blockname=blockname.strip()
        blockname_tf=commonTools.check_tf_variable(blockname)
        compartmentVarName=compartmentVarName.strip()
        compartmentVarName = commonTools.check_tf_variable(compartmentVarName)

        tempStr = """resource "oci_core_volume"  \"""" + blockname_tf + """"  {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var.""" + compartmentVarName + """}"

        #Optional
        display_name = \"""" + blockname + """"
        size_in_gbs = \"""" + size + """"
        ## Defined Tag Info ##
        }

resource "oci_core_volume_attachment" \"""" + blockname_tf + """_volume_attachment" {
        #Required
        instance_id = "${oci_core_instance.""" + attacheToInstanceName + """.id}"
        attachment_type = \"""" + attachType + """"
        volume_id = "${oci_core_volume.""" + blockname_tf + """.id}"

        }
        
        """
        outfile = outdir+"/"+region+"/"+blockname+".tf"
        print("Writing " + outfile)
        oname = open(outfile,"w")
        oname.write(tempStr)
        oname.close()



#If input is a csv file
elif('.csv' in filename):
    fname = open(filename, "r")
    all_regions = os.listdir(outdir)
    for line in fname:
        if not line.startswith('#'):
            #[block_name,size_in_gb,availability_domain(AD1|AD2|AD3),attached_to_instance,attach_type(iscsi|paravirtualized,compartment_var_name] = line.split(',')
            linearr = line.split(",")
            region=linearr[0].strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                continue

            blockname = linearr[1].strip()
            size = linearr[2].strip()
            AD = linearr[3].strip()
            attacheToInstanceName = linearr[4].strip()
            attachType = linearr[5].strip()
            compartmentVarName = linearr[6].strip()
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
            outfile = outdir+"/"+region+"/"+blockname+".tf"
            oname = open(outfile,"w")
            oname.write(tempStr)
            oname.close()
    fname.close()
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

