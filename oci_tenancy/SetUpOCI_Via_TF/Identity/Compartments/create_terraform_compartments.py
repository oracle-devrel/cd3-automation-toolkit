#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import os
import pandas as pd

######
# Required Inputs- Either properties file: vcn-info.properties or CD3 excel file AND Outfile
# if properties file is the input then Code will read input compartment file name from Default Section
# Compartments are defined in csv format
# outfile is the name of output terraform file generated
######


parser = argparse.ArgumentParser(description="Create Compartments terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the csv file or CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir=args.outdir
prefix=args.prefix

ash_dir=outdir+"/ashburn"
phx_dir=outdir+"/phoenix"

if not os.path.exists(ash_dir):
        os.makedirs(ash_dir)

if not os.path.exists(phx_dir):
        os.makedirs(phx_dir)
outfile_ash=ash_dir + "/" + prefix + '-compartments.tf'
outfile_phx=phx_dir + "/" + prefix + '-compartments.tf'

tempStrASH = ""
tempStrPHX = ""

if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='Compartments',skiprows=1)
    df.dropna(how='all')
    NaNstr = 'NaN'
    endNames = {'<END>', '<end>'}

    for i in df.index:
        region = df.iat[i,0]

        if (region in endNames):
            break

        compartment_name = df.iat[i, 1]


        compartment_desc = df.iat[i, 2]
        parent_compartment_name = df.iat[i, 3]
        if (str(parent_compartment_name).lower()== NaNstr.lower() or parent_compartment_name.lower() == 'root'):
            parent_compartment='${var.tenancy_ocid}'
        else:
            parent_compartment='${oci_identity_compartment.'+parent_compartment_name.strip()+'.id}'
        if (str(compartment_name).lower() != NaNstr.lower()):
            region = region.strip().lower()

            compartment_name = compartment_name.strip()
            if (str(compartment_desc).lower() == NaNstr.lower()):
                compartment_desc = compartment_name
            if(region=='ashburn'):
                tempStrASH=tempStrASH + """
resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
	    compartment_id = \"""" + parent_compartment + """"
	    description = \"""" + compartment_desc.strip() + """"
  	    name = \"""" + compartment_name.strip() + """"
} """
            if (region == 'phoenix'):
                tempStrPHX = tempStrPHX + """
            resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
            	    compartment_id = \"""" + parent_compartment + """"
            	    description = \"""" + compartment_desc.strip() + """"
              	    name = \"""" + compartment_name.strip() + """"

            	} """

#If input is a csv file
elif('.csv' in args.inputfile):
    compartment_file_name = args.inputfile
    fname = open(compartment_file_name, "r")

    endNames = {'<END>', '<end>'}

    # Read compartment file
    for line in fname:
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [region,compartment_name, compartment_desc, parent_compartment_name] = line.split(',')
            region=region.strip().lower()
            compartment_name=compartment_name.strip()
            compartment_desc=compartment_desc.strip()
            parent_compartment_name=parent_compartment_name.strip()

            if (parent_compartment_name.strip() == '' or parent_compartment_name.lower() == 'root'):
                parent_compartment = '${var.tenancy_ocid}'
            else:
                parent_compartment = '${oci_identity_compartment.' + parent_compartment_name + '.id}'

            if(compartment_name.strip()!='Name' and compartment_name.strip()!=''):
                if (compartment_desc.strip() == ''):
                    compartment_desc = compartment_name
                if(region=='ashburn'):
                    tempStrASH=tempStrASH + """
resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
        compartment_id = \"""" + parent_compartment + """"
        description = \"""" + compartment_desc.strip() + """"
  	    name = \"""" + compartment_name.strip() + """"
} """
                if (region == 'phoenix'):
                    tempStrPHX = tempStrPHX + """
                resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
                        compartment_id = \"""" + parent_compartment + """"
                        description = \"""" + compartment_desc.strip() + """"
                  	    name = \"""" + compartment_name.strip() + """"

                    } """
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

if(tempStrASH!=''):
    oname_ash = open(outfile_ash, "w")
    oname_ash.write(tempStrASH)
    oname_ash.close()
    print(outfile_ash + " containing TF for compartments has been created")

if(tempStrPHX!=''):
    oname_phx = open(outfile_phx, "w")
    oname_phx.write(tempStrASH)
    oname_phx.close()
    print(outfile_phx + " containing TF for compartments has been created")


